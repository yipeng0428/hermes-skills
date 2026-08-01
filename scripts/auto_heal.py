#!/usr/bin/env python3
"""
Hermes Auto-Heal — 中断自愈系统 v1.0
=====================================
免费 API 报错 → 自动切换其它可用模型 → 自动恢复未完成工作，全程无需人工确认。

三层防线:
  L1 静态防线:  健康 fallback 链 (config.yaml fallback_model, 由本脚本维护)
  L2 动态防线:  定时健康巡检, 自动把死模型摘出 fallback 链 / 恢复的加回
  L3 中断自愈:  检测中断会话 → 自动切换主模型 → 自动 resume 未完成任务

运行模式:
  python auto_heal.py --check     # 仅巡检 fallback 链健康度并修复 (L1+L2)
  python auto_heal.py --heal      # 巡检 + 中断检测 + 自动恢复 (L1+L2+L3)
  python auto_heal.py --status    # 查看当前健康状态 (只读)

Cron 建议: no_agent=true, 每 5-10 分钟跑一次 --heal。
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
HEALTH_SCRIPT = Path.home() / ".hermes/scripts/quick_health_check.py"
HERMES_EXE = str(HERMES_HOME / "hermes-agent/venv/Scripts/hermes.exe")

# 判断"死模型"的错误关键词(免费 API 常见花式报错)
DEAD_KEYWORDS = [
    "401", "403", "405", "429", "insufficient", "quota", "balance",
    "unauthorized", "invalid api key", "expired", "not found", "404",
    "model not", "不存在", "无权", "余额", "已过期",
]
# 明确的"临时故障"关键词(不该摘除, 重试即可)
TRANSIENT_KEYWORDS = ["timeout", "timed out", "502", "503", "529", "connection", "overloaded", "繁忙", "访问量过大"]


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


def provider_available(provider: str, health: list) -> bool:
    """健康结果里该 provider 是否可用。provider 可能是 custom:qwen1 形式。"""
    for h in health:
        hp = str(h.get("provider", ""))
        if hp == provider or hp == provider.replace("custom:", ""):
            if classify_status(h) == "ok":
                return True
    return False


def get_health_for(provider: str, health: list) -> dict | None:
    for h in health:
        hp = str(h.get("provider", ""))
        if hp == provider or hp == provider.replace("custom:", ""):
            return h
    return None


def fix_fallback_chain(health: list, cfg: dict) -> tuple[list, list]:
    """重排 fallback_model: 死模型摘除, 恢复的加回, 按延迟排序。返回 (新链, 变更说明)。"""
    chain = cfg.get("fallback_model", [])
    if not isinstance(chain, list):
        chain = []
    changes = []

    # 1. 摘除死模型
    alive = []
    for entry in chain:
        provider = str(entry.get("provider", "")).strip()
        h = get_health_for(provider, health)
        if h is None:
            alive.append(entry)  # 没测到, 保持
            continue
        cls = classify_status(h)
        if cls == "dead":
            changes.append(f"摘除死模型: {provider}/{entry.get('model','')} ({h.get('error','')[:60]})")
            continue
        alive.append(entry)

    # 2. 把健康但不在链里的 provider 加回(按延迟排序追加)
    in_chain = {str(e.get("provider", "")).replace("custom:", "") for e in alive}
    healthy_extra = []
    for h in health:
        if classify_status(h) != "ok":
            continue
        hp = str(h.get("provider", ""))
        if hp in in_chain or hp == "ollama":
            continue
        # 找该 provider 的默认模型
        entry = {"provider": f"custom:{hp}" if hp in ("qwen1", "qwen2") else hp,
                 "model": str(h.get("model", ""))}
        if entry["model"]:
            healthy_extra.append((h.get("latency", 999), entry))
    healthy_extra.sort(key=lambda x: x[0])
    for _, entry in healthy_extra:
        alive.append(entry)
        changes.append(f"加回健康模型: {entry['provider']}/{entry['model']}")

    # 3. 排序: 保持原链顺序(用户偏好), 新加的在末尾
    new_chain = alive
    if new_chain != chain:
        cfg["fallback_model"] = new_chain
        save_config(cfg)
        changes.append("fallback 链已更新")

    return new_chain, changes


def ensure_primary_healthy(cfg: dict, health: list) -> tuple[str, list]:
    """主模型挂了 → 自动切换到当前最健康、延迟最低的可用模型。返回 (动作, 说明)。"""
    changes = []
    provider = str(cfg.get("model", {}).get("provider", ""))
    model = str(cfg.get("model", {}).get("default", ""))
    h = get_health_for(provider, health)
    if h is not None and classify_status(h) == "ok":
        return "keep", changes
    if h is None:
        return "keep", changes  # 没测到, 不动

    # 主模型不可用 → 找最优替代
    best = None
    for cand in health:
        if classify_status(cand) != "ok":
            continue
        hp = str(cand.get("provider", ""))
        if hp == "ollama":
            continue
        lat = cand.get("latency", 999)
        if best is None or lat < best[0]:
            best = (lat, hp, str(cand.get("model", "")))
    if best is None:
        changes.append(f"⚠️ 主模型 {provider}/{model} 不可用且无健康替代, 需要人工介入")
        return "none", changes

    lat, new_provider, new_model = best
    new_provider_cfg = f"custom:{new_provider}" if new_provider in ("qwen1", "qwen2") else new_provider
    cfg.setdefault("model", {})["provider"] = new_provider_cfg
    cfg["model"]["default"] = new_model
    save_config(cfg)
    changes.append(f"🔁 主模型自动切换: {provider}/{model} → {new_provider_cfg}/{new_model} (延迟{lat}s)")
    return "switched", changes


# ─────────────────────────────────────────────────────────────
# L3: 中断检测 + 自动恢复
# ─────────────────────────────────────────────────────────────
def detect_interrupted_sessions(minutes: int = 30) -> list:
    """扫描 state.db, 找最近 minutes 分钟内"中断"的会话。

    判据:
      - 会话最近一条 assistant 消息 finish_reason='error'
      - 或会话 end_reason 为异常值 (agent_close/ws_orphan_reap 且消息里带错误)
      - 且会话未正常完成 (最后一条不是正常 stop 回复)
    """
    if not STATE_DB.exists():
        return []
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


def resume_session(session_id: str, provider: str, model: str, task_hint: str = "") -> tuple[bool, str]:
    """用指定模型自动恢复中断会话, 让它把未完成的工作继续做完。"""
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


# ─────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Hermes Auto-Heal 中断自愈系统")
    ap.add_argument("--check", action="store_true", help="仅巡检 fallback 链 (L1+L2)")
    ap.add_argument("--heal", action="store_true", help="巡检 + 中断自愈 (L1+L2+L3, 默认模式)")
    ap.add_argument("--status", action="store_true", help="只读状态")
    args = ap.parse_args()

    # 无参数 → 默认 heal (cron 直接调用)
    mode = "heal" if (args.heal or not (args.check or args.status)) else ("check" if args.check else "status")

    # 1. 健康巡检
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

    output = []

    # 2. L1+L2: fallback 链修复
    cfg = load_config()
    new_chain, chain_changes = fix_fallback_chain(health, cfg)
    output.extend(chain_changes)

    # 主模型健康保障
    action, primary_changes = ensure_primary_healthy(cfg, health)
    output.extend(primary_changes)

    # 3. L3: 中断检测 + 自动恢复 (仅 --heal)
    if mode == "heal":
        interrupted = detect_interrupted_sessions(minutes=30)
        if interrupted:
            # 找当前最优健康模型用于恢复
            best = None
            for h in health:
                if classify_status(h) != "ok":
                    continue
                if str(h.get("provider", "")) == "ollama":
                    continue
                lat = h.get("latency", 999)
                if best is None or lat < best[0]:
                    best = (lat, str(h.get("provider", "")), str(h.get("model", "")))
            if best:
                _, prov, model = best
                provider_cfg = f"custom:{prov}" if prov in ("qwen1", "qwen2") else prov
                for sess in interrupted:
                    ok, msg = resume_session(sess["session_id"], provider_cfg, model, sess["reason"])
                    output.append(f"🛠️ 自动恢复会话 {sess['session_id']} ({sess['title']}) "
                                  f"用 {provider_cfg}/{model}: {'✅ ' + msg if ok else '❌ ' + msg}")

    # 4. 输出(空 = 静默, 有 = 通知)
    if output:
        for line in output:
            log(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
