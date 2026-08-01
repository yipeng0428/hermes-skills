---
name: auto-heal
description: "AI 中断自愈系统: API 报错自动切换模型并恢复任务。触发词: 中断自愈、auto-heal、自动切换模型。"
version: 1.0.0
author: Hermes·公司
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, fallback, self-heal, provider, automation]
---

# Auto-Heal 中断自愈系统

## 解决的问题

免费 API 报错（401/405/429/解析失败/空响应等花式错误）→ Hermes 会话中断 →
传统方案需要人工点选确认继续。本系统让中断**自动**切换其它可用模型并**自动**
恢复未完成任务，全程静默，无需人工介入。

## 三层防线架构

```
L1 静态防线  健康 fallback 链 (config.yaml fallback_model)
L2 动态防线  定时健康巡检 → 死模型摘除 / 恢复的加回 / 按延迟排序
L3 中断自愈  检测中断会话 → 自动切换主模型 → hermes chat --continue 自动恢复
```

## 核心文件

| 文件 | 作用 |
|------|------|
| `E:\hermes\scripts\auto_heal.py` | 自愈主脚本（唯一需要维护的文件） |
| cron job `🩺 AI 中断自愈巡检` | 每 10 分钟 `*/10 * * * *` 跑一次，no_agent=true |

## 运行模式

```bash
python E:/hermes/scripts/auto_heal.py --status   # 只读健康状态
python E:/hermes/scripts/auto_heal.py --check    # 仅修复 fallback 链 (L1+L2)
python E:/hermes/scripts/auto_heal.py --heal     # 全流程 (默认, cron 直接调用)
```

**输出约定**: 空输出=一切正常(静默); 有输出=自愈动作或异常(通知)。cron 用
no_agent=true 直接投递 stdout。

## 关键技术发现（2026-08-01 实测）

1. **Hermes 内置 fallback 只覆盖有限错误**: 429/529/503/连接超时
   (`_TRANSIENT_TRANSPORT_ERRORS` = ReadTimeout/ConnectTimeout/PoolTimeout/
   ConnectError/RemoteProtocolError/APIConnectionError/APITimeoutError)。
   免费 API 的 401/405/解析错误/空响应**不在触发范围** → 直接中断。
2. **桌面会话可被 CLI 完全接管恢复**: `hermes chat --continue <session_id>
   -q "继续完成" --provider X -m Y` 可以从命令行恢复桌面端会话并追加消息。
   这是 L3 自动恢复的通道，已实测成功。
3. **会话中断判据** (state.db sessions/messages 表):
   - 最后一条 assistant 消息 `finish_reason='error'` ✅ 可靠
   - `end_reason` 异常 (agent_close/ws_orphan_reap) + 末尾含 error 关键词
   - 注意: `agent_close` 也可能是用户主动关闭，需配合错误关键词判断
4. **死模型会阻塞 fallback 链**: jbbtoken 405 失效后仍排第 2 位，触发
   fallback 时直接卡死。健康巡检必须持续维护链。
5. **主模型配置**: config.yaml 的 `model.provider` 用 `custom:qwen1` 形式
   (自定义 provider 前缀)，健康检查脚本返回的是裸名 `qwen1`，转换逻辑
   已内置于脚本。

## 维护要点

- 新加 provider 后: 先跑 `auto_heal.py --status` 确认被正确识别
- 健康检查脚本 `quick_health_check.py` 在 `~/.hermes/scripts/`，
  MSYS bash 里 `python ~/.hermes/...` 会路径转换出错，要用
  `python "C:/Users/win10/.hermes/scripts/quick_health_check.py"`
- 修改 auto_heal.py 后 cron 无需重启（脚本每次实时执行）
- 手动测试中断恢复: 往 state.db 插一条 finish_reason='error' 的会话，
  跑 `--heal`，验证恢复后检查 messages 表出现新轮次

## 验证清单

- [ ] `--status` 显示各 provider 状态 (✅/💀/⚠️/❔)
- [ ] `--check` 能自动把死模型移出 fallback 链
- [ ] 模拟中断会话 → `--heal` 自动恢复成功 (messages 出现新 assistant 轮次)
- [ ] cron 手动触发 last_status=ok
