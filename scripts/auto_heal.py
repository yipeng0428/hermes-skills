#!/usr/bin/env python3
"""
Hermes Auto-Heal — 中断自愈系统 v2.0
=====================================
免费 API 报错 → 自动切换其它可用模型 → 自动恢复未完成工作，全程无需人工确认。

v2.0 关键升级 (2026-08-01):
  ✅ L3b 实时错误日志检测 — 扫描 logs/errors.log 中的 API 失败
     (403/401/405/quota exhausted/Non-retryable/Streaming failed)
     修复 v1 盲区: v1 只看 state.db finish_reason='error'，
     但真实中断时会话 finish_reason 仍是 tool_calls (turn 内失败) → 漏检!
  ✅ 死模型自动摘除 — errors.log 中出现 quota exhausted / 403 等
     → 立即从 fallback 链摘除, 不等健康巡检
  ✅ --fast 快速模式 — 只扫日志+摘死模型+恢复受影响会话 (秒级, 适合高频轮询)

三层防线:
  L1 静态防线:  健康 fallback 链 (config.yaml fallback_model, 由本脚本维护)
  L2 动态防线:  定时健康巡检, 自动把死模型摘出 fallback 链 / 恢复的加回
  L3 中断自愈:  检测中断会话 → 自动切换主模型 → 自动 resume 未完成任务
                 L3a: state.db 判据 (finish_reason=error / end_reason 异常)
                 L3b: errors.log 实时判据 (API 调用失败日志, v2.0 新增)

运行模式:
  python auto_heal.py --check     # 仅巡检 fallback 链健康度并修复 (L1+L2)
  python auto_heal.py --heal      # 巡检 + 中断检测 + 自动恢复 (L1+L2+L3, 默认)
  python auto_heal.py --fast      # 快速模式: 只扫 errors.log + 摘死模型 + 恢复 (秒级)
  python auto_heal.py --status    # 查看当前健康状态 (只读)

Cron 建议: no_agent=true
  每 2 分钟: auto_heal.py --fast   (实时响应)
  每 10 分钟: auto_heal.py --heal  (全量巡检)
空输出 = 一切正常 (静默); 有输出 = 发生了自愈动作或异常, 通知用户。
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "E:/hermes"))
CONFIG_PATH = HERMES_HOME / "config.yaml"
STATE_DB = HERMES_HOME / "state.db"
ERRORS_LOG = HERMES_HOME / "logs/errors.log"
HEALTH_SCRIPT = Path.home() / ".hermes/scripts/quick_health_check.py"
HERMES_EXE = str(HERMES_HOME / "hermes-agent/venv/Scripts/hermes.exe")

# 判断"死模型"的错误关键词(免费 API 常见花式报错)
DEAD_KEYWORDS = [
    "401", "403", "405", "insufficient", "quota", "balance",
    "unauthorized", "invalid api key", "expired", "not found", "404",
    "model not", "不存在", "无权", "余额", "已过期", "quota exhausted",
    "free tier", "allocationquota", "permissiondenied",
]
# 明确的"临时故障"关键词(不该摘除, 重试即可)
TRANSIENT_KEYWORDS = ["timeout", "timed out", "502", "503", "529", "connection", "overloaded", "繁忙", "访问量过大"]

# errors.log 中代表"API 调用失败"的行特征
LOG_FAIL_PATTERNS = [
    r"API call failed",
    r"Non-retryable client error",
    r"Streaming failed before delivery",
    r"all retries exhausted",
    r"Connection error",
    r"APIConnectionError",
    r"RateLimitError",
    r"AuthenticationError",
    r"PermissionDeniedError",
    r"BadRequestError",
    r"NotFoundError",
]


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[auto-heal {ts}] {msg}", flush=True)


# ─────────────────────────────────────────────────────────────
# L1+L2: 健康巡检 + fallback 链自动修复
# ─────────────────────────────────────────────────────────────
def run_health_check(timeout: int = 240) -> list:
    """运行 quick_health_check.py, 解析 JSON 结果。"""
    if not HEALTH_SCRIPT.exists():
        # 尝试从 E:\hermes\scripts 找
        alt = HERMES_HOME / "scripts/quick_health_check.py"
        if alt.exists():
            HEALTH_SCRIPT_USE = alt
        else:
            log(f"⚠️ 健康检查脚本不存在: {HEALTH_SCRIPT}")
            return []
    else:
        HEALTH_SCRIPT_USE = HEALTH_SCRIPT
    try:
        proc = subprocess.run(
            [sys.executable, str(HEALTH_SCRIPT_USE)],
            capture_output=True, text=True, timeout=timeout,
        )
        out = proc.stdout
        # 提取 ---JSON--- 之后的部分
        marker = "---JSON---"
        if marker in out:
            out = out.split(marker, 1)[1]
        data = json.loads(out)
        return data if isinstance(data, list) else []
    except Exception as e:
        log(f"⚠️ 健康检查失败: {e}")
        return []


def classify_status(entry: dict) -> str:
    """把健康检查条目归类为 ok / dead / transient / unknown。"""
    status = str(entry.get("status", "")).lower()
    if status == "ok":
        return "ok"
    err = str(entry.get("error", ""))
    if status in ("no_key",):
        return "unknown"  # 没配 key, 保持现状
    if status in ("unreachable", "server_error"):
        return "transient"  # 连接/服务端问题, 可能恢复
    if status in ("rate_limited",):
        return "transient"
    if status in ("unauthorized", "not_found"):
        return "dead"
    # 按错误文本判断
    if any(k.lower() in err.lower() for k in DEAD_KEYWORDS):
        # 429/繁忙属于 transient, 但连续多次才摘除, 这里先归 transient
        if any(k.lower() in err.lower() for k in ["429", "overloaded", "繁忙", "访问量过大"]):
            return "transient"
        return "dead"
    if any(k.lower() in err.lower() for k in TRANSIENT_KEYWORDS):
        return "transient"
    if err:
        return "dead"  # 有错误但无法归类 → 视为死
    return "unknown"


def load_config() -> dict:
    import yaml
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg: dict) -> None:
    import yaml
    CONFIG_PATH.write_text(
        yaml.dump(cfg, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def fix_fallback_chain(health: list, cfg: dict) -> tuple:
    """根据健康数据重排 fallback 链: 移除 dead, 按延迟排序。返回 (新链, 变更描述)。"""
    chain = cfg.get("fallback_model", [])
    if not chain:
        return chain, []
    changes = []

    # 建 provider → (latency, status) 映射
    info = {}
    for h in health:
        prov = str(h.get("provider", ""))
        info[prov] = (h.get("latency", 999), classify_status(h))

    dead_in_chain = []
    for entry in chain:
        prov = entry.get("provider", "")
        # 去掉 custom: 前缀做匹配
        key = prov.replace("custom:", "")
        status = info.get(key, ("?", "unknown"))[1]
        if status == "dead":
            dead_in_chain.append(prov)
    if dead_in_chain:
        new_chain = [e for e in chain if e.get("provider", "") not in dead_in_chain]
        cfg["fallback_model"] = new_chain
        save_config(cfg)
        changes.append(f"💀 已从 fallback 链移除死模型: {', '.join(dead_in_chain)}")

    # 活着且有序: 按延迟重排
    alive = [e for e in cfg["fallback_model"]]
    keyed = []
    for e in alive:
        prov = e.get("provider", "").replace("custom:", "")
        lat = info.get(prov, (999, "unknown"))[0]
        keyed.append((lat, e))
    keyed.sort(key=lambda x: x[0])
    sorted_chain = [e for _, e in keyed]
    if sorted_chain != cfg["fallback_model"]:
        cfg["fallback_model"] = sorted_chain
        save_config(cfg)
        changes.append("🔀 fallback 链已按延迟重排: " + " → ".join(e.get("provider", "?") for e in sorted_chain))
    return cfg["fallback_model"], changes


def ensure_primary_healthy(cfg: dict, health: list) -> tuple:
    """如果主模型挂了, 自动切到当前最优健康模型。返回 (动作, 变更描述)。"""
    model_cfg = cfg.get("model", {})
    cur_prov = str(model_cfg.get("provider", ""))
    cur_model = str(model_cfg.get("default", ""))
    info = {}
    for h in health:
        prov = str(h.get("provider", ""))
        info[prov] = (h.get("latency", 999), classify_status(h))
    key = cur_prov.replace("custom:", "")
    cur_status = info.get(key, (999, "unknown"))[1]
    if cur_status != "dead":
        return "none", []
    # 主模型死了 → 找最优
    best = None
    for h in health:
        if classify_status(h) != "ok":
            continue
        if str(h.get("provider", "")) == "ollama":
            continue
        lat = h.get("latency", 999)
        if best is None or lat < best[0]:
            best = (lat, str(h.get("provider", "")), str(h.get("model", "")))
    if not best:
        return "none", [f"⚠️ 主模型 {cur_prov}/{cur_model} 已死, 但无可用替补!"]
    _, prov, model = best
    model_cfg["provider"] = prov
    model_cfg["default"] = model
    save_config(cfg)
    return "switched", [f"🔁 主模型 {cur_prov}/{cur_model} 已死, 自动切换为 {prov}/{model}"]


# ─────────────────────────────────────────────────────────────
# L3a: state.db 中断会话检测 (v1 逻辑)
# ─────────────────────────────────────────────────────────────
def detect_interrupted_sessions(minutes: int = 30) -> list:
    try:
        conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
        since = time.time() - minutes * 60
        rows = conn.execute(
            """SELECT s.id, s.title, s.end_reason, s.message_count,
                      (SELECT content FROM messages m WHERE m.session_id = s.id
                       AND m.role='assistant' ORDER BY m.id DESC LIMIT 1) AS last_content,
                      (SELECT finish_reason FROM messages m WHERE m.session_id = s.id
                       AND m.role='assistant' ORDER BY m.id DESC LIMIT 1) AS last_finish
               FROM sessions s
               WHERE s.started_at > ? AND s.source != 'cron'
               ORDER BY s.started_at DESC LIMIT 20""",
            (since,),
        ).fetchall()
        conn.close()
    except Exception as e:
        log(f"⚠️ state.db 读取失败: {e}")
        return []

    interrupted = []
    for sid, title, end_reason, msg_count, last_content, last_finish in rows:
        if not sid:
            continue
        # 判据1: 最后一条 assistant 消息 finish_reason='error'
        if last_finish == "error":
            interrupted.append({"session_id": sid, "title": title or "(无标题)",
                                "reason": "assistant finish_reason=error"})
            continue
        # 判据2: 异常结束且最后消息含错误特征
        if end_reason in ("agent_close", "ws_orphan_reap") and last_content:
            txt = str(last_content)[-500:]
            if any(k.lower() in txt.lower() for k in ["error", "失败", "exception", "traceback", "internal error"]):
                interrupted.append({"session_id": sid, "title": title or "(无标题)",
                                    "reason": f"end_reason={end_reason} 且末尾含错误"})
    return interrupted


# ─────────────────────────────────────────────────────────────
# L3b: errors.log 实时错误检测 (v2.0 新增 — 修复 v1 盲区)
# ─────────────────────────────────────────────────────────────
def scan_errors_log(minutes: int = 30, tail_lines: int = 20000) -> dict:
    """
    扫描 errors.log 最近 minutes 分钟内的 API 失败。
    返回: {
      "dead_providers": [provider...],     # 出现 quota/403/401 等永久死信号
      "interrupted_sessions": [{session_id, title, reason}...],  # 日志中受影响的会话
      "fail_count": int
    }
    """
    result = {"dead_providers": [], "interrupted_sessions": [], "fail_count": 0}
    if not ERRORS_LOG.exists():
        return result

    try:
        lines = ERRORS_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        log(f"⚠️ errors.log 读取失败: {e}")
        return result

    cutoff = time.time() - minutes * 60
    seen_sessions = set()
    dead_seen = set()
    session_title_cache = {}

    # 倒序扫描(最新优先), 只处理时间窗口内的行
    for line in reversed(lines[-tail_lines:]):
        m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if not m:
            continue
        try:
            ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            if ts.timestamp() < cutoff:
                break  # 倒序遇到窗口外 → 结束
        except ValueError:
            continue

        # 是否 API 失败行?
        is_fail = any(p.lower() in line.lower() for p in LOG_FAIL_PATTERNS)
        if not is_fail:
            continue

        result["fail_count"] += 1

        # 提取 provider (provider=custom:qwen1 或 provider=longcat)
        pm = re.search(r"provider=([\w:-]+)", line)
        if pm:
            prov = pm.group(1).replace("custom:", "")
            if any(k.lower() in line.lower() for k in DEAD_KEYWORDS):
                if prov not in dead_seen:
                    dead_seen.add(prov)
                    result["dead_providers"].append(prov)

        # 提取会话 id ([20260801_143554_491755] 或 session_id=...)
        sm = re.search(r"\[(\d{8}_\d{6}_[a-z0-9]+)\]", line)
        if not sm:
            sm = re.search(r"session_id=([\w]+)", line)
        if sm:
            sid = sm.group(1)
            if sid not in seen_sessions:
                seen_sessions.add(sid)
                # 从 state.db 拿标题
                title = session_title_cache.get(sid, "(日志会话)")
                try:
                    conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
                    r = conn.execute("SELECT title FROM sessions WHERE id=?", (sid,)).fetchone()
                    conn.close()
                    if r and r[0]:
                        title = r[0]
                except Exception:
                    pass
                result["interrupted_sessions"].append({
                    "session_id": sid, "title": title,
                    "reason": f"errors.log API 失败 (最近{minutes}分钟)"
                })
    return result


# ─────────────────────────────────────────────────────────────
# L3: 会话恢复
# ─────────────────────────────────────────────────────────────
LOCK_FILE = HERMES_HOME / "tmp/auto_heal.lock"


def acquire_lock(timeout: int = 5) -> bool:
    """单实例锁: 防止多个 cron 并发执行自愈 (v2.1 防递归关键)。"""
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        if LOCK_FILE.exists():
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age > 1800:  # 锁超过30分钟视为死锁, 强制覆盖
                LOCK_FILE.unlink()
            else:
                return False
        LOCK_FILE.write_text(str(time.time()))
        return True
    except Exception:
        return False


def release_lock() -> None:
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def is_active_session(session_id: str, idle_threshold: int = 120) -> bool:
    """
    v2.1 关键保护: 判断会话是否"活跃" (正在被用户/桌面端交互)。
    活跃会话绝不自动恢复 — 避免递归自愈 (恢复指令注入正在运行的会话 → 新调用 → 又失败 → 又注入)。
    判据: end_reason IS NULL 且最近 idle_threshold 秒内有新消息 = 正在使用。
    """
    try:
        conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
        row = conn.execute(
            "SELECT end_reason FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
        if not row:
            conn.close()
            return False
        if row[0] is not None:
            conn.close()
            return False  # 已结束的会话, 可以恢复
        # 会话未结束 → 看最近是否有新消息
        r = conn.execute(
            "SELECT MAX(timestamp) FROM messages WHERE session_id=?",
            (session_id,),
        ).fetchone()
        conn.close()
        last_ts = r[0] if r and r[0] else 0
        return (time.time() - last_ts) < idle_threshold
    except Exception:
        return True  # 无法判断 → 保守: 视为活跃, 不恢复


def resume_session(session_id: str, provider: str, model: str, task_hint: str = "") -> tuple[bool, str]:
    """用指定模型自动恢复中断会话, 让它把未完成的工作继续做完。"""
    # v2.1: 活跃会话保护 — 正在交互的会话绝不自动恢复
    if is_active_session(session_id):
        return False, "会话活跃中(有用户交互), 跳过自动恢复"
    prompt = (f"【自动恢复】你刚才的任务因 API 中断而停止。请检查会话历史, "
              f"继续完成未完成的工作, 直到任务真正完成。")
    if task_hint:
        prompt += f"\n任务背景: {task_hint}"
    cmd = [
        HERMES_EXE, "chat", "--continue", session_id,
        "-q", prompt,
        "--provider", provider, "-m", model,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode == 0:
            return True, "恢复完成"
        # 失败时看有没有输出
        tail = (proc.stdout or "")[-300:] + (proc.stderr or "")[-300:]
        return False, tail[-400:]
    except subprocess.TimeoutExpired:
        return False, "恢复超时(600s)"
    except Exception as e:
        return False, str(e)


def pick_best_model(health: list) -> tuple:
    """从健康池中选最优恢复模型 (跳过 ollama 本地)。返回 (provider, model)。"""
    best = None
    for h in health:
        if classify_status(h) != "ok":
            continue
        if str(h.get("provider", "")) == "ollama":
            continue
        lat = h.get("latency", 999)
        if best is None or lat < best[0]:
            best = (lat, str(h.get("provider", "")), str(h.get("model", "")))
    if not best:
        return None, None
    _, prov, model = best
    provider_cfg = f"custom:{prov}" if prov in ("qwen1", "qwen2") else prov
    return provider_cfg, model


# ─────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Hermes Auto-Heal 中断自愈系统 v2.0")
    ap.add_argument("--check", action="store_true", help="仅巡检 fallback 链 (L1+L2)")
    ap.add_argument("--heal", action="store_true", help="巡检 + 中断自愈 (L1+L2+L3, 默认模式)")
    ap.add_argument("--fast", action="store_true", help="快速模式: 扫 errors.log + 摘死模型 + 恢复 (秒级)")
    ap.add_argument("--status", action="store_true", help="只读状态")
    args = ap.parse_args()

    # 无参数 → 默认 heal
    mode = "heal"
    if args.fast:
        mode = "fast"
    elif args.check:
        mode = "check"
    elif args.status:
        mode = "status"

    # v2.1: 单实例锁 — 防并发递归 (多个 cron 同时触发)
    if mode in ("fast", "heal") and not acquire_lock():
        return 0  # 另一个实例在跑, 静默退出
    try:
        return _run(mode, [])
    finally:
        release_lock()


def _run(mode: str, output: list) -> int:
    if mode == "fast":
        # ── 快速模式: 不跑完整健康检查, 直接扫日志 (秒级) ──
        log_scan = scan_errors_log(minutes=10)
        if log_scan["fail_count"] == 0:
            return 0  # 完全静默
        output.append(f"⚠️ 最近10分钟 errors.log 检测到 {log_scan['fail_count']} 次 API 失败")

        # 死模型 → 从 fallback 链摘除
        cfg = load_config()
        if log_scan["dead_providers"]:
            chain = cfg.get("fallback_model", [])
            dead = log_scan["dead_providers"]
            removed = [e.get("provider", "") for e in chain
                       if e.get("provider", "").replace("custom:", "") in dead]
            if removed:
                cfg["fallback_model"] = [e for e in chain if e.get("provider", "") not in removed]
                save_config(cfg)
                output.append(f"💀 日志显示死模型, 已从 fallback 链移除: {', '.join(removed)}")

        # 主模型若在死列表 → 切换 (用最近的健康检查数据, 不重跑完整检查)
        model_cfg = cfg.get("model", {})
        cur_prov = str(model_cfg.get("provider", "")).replace("custom:", "")
        if cur_prov in log_scan["dead_providers"]:
            # 快速健康检查找替补 (限时 90s)
            health = run_health_check(timeout=90)
            prov, model = pick_best_model(health)
            if prov:
                model_cfg["provider"] = prov
                model_cfg["default"] = model
                save_config(cfg)
                output.append(f"🔁 主模型 {cur_prov} 已死(日志确认), 切换为 {prov}/{model}")

        # v2.1: fast 模式不自动恢复会话 (只摘死模型+切主模型)
        # 恢复动作留给 heal 深度模式, 且 heal 有活跃会话保护
        if output:
            for line in output:
                log(line)
        return 0

    # ── 完整模式 (check / heal / status): 先跑健康巡检 ──
    health = run_health_check()
    if not health:
        log("⚠️ 无法获取健康数据, 本次跳过")
        return 1

    if mode == "status":
        for h in health:
            cls = classify_status(h)
            mark = {"ok": "✅", "dead": "💀", "transient": "⚠️", "unknown": "❔"}[cls]
            print(f"{mark} {h.get('provider')}/{h.get('model')} [{h.get('status')}] "
                  f"延迟{h.get('latency', '?')}s {h.get('error', '')[:80]}")
        return 0

    # 1. L1+L2: fallback 链修复
    cfg = load_config()
    new_chain, chain_changes = fix_fallback_chain(health, cfg)
    output.extend(chain_changes)

    # 主模型健康保障
    action, primary_changes = ensure_primary_healthy(cfg, health)
    output.extend(primary_changes)

    # 2. L3: 中断检测 + 自动恢复
    if mode == "heal":
        # L3a: state.db 判据
        interrupted = detect_interrupted_sessions(minutes=30)
        # L3b: errors.log 判据 (v2.0)
        log_scan = scan_errors_log(minutes=10)
        if log_scan["fail_count"] > 0:
            output.append(f"⚠️ 最近10分钟 errors.log 有 {log_scan['fail_count']} 次 API 失败")
        # 合并: 日志中出现的会话也视为中断 (去重)
        log_sessions = {s["session_id"] for s in log_scan["interrupted_sessions"]}
        for s in log_scan["interrupted_sessions"]:
            if s["session_id"] not in {x["session_id"] for x in interrupted}:
                interrupted.append(s)

        if interrupted:
            prov, model = pick_best_model(health)
            if prov:
                for sess in interrupted:
                    # v2.1: 活跃会话保护在 resume_session 内部
                    ok, msg = resume_session(sess["session_id"], prov, model, sess["reason"])
                    output.append(f"🛠️ 自动恢复会话 {sess['session_id']} ({sess['title']}) "
                                  f"用 {prov}/{model}: {'✅ ' + msg if ok else '❌ ' + msg}")

    # 3. 输出(空 = 静默, 有 = 通知)
    if output:
        for line in output:
            log(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
