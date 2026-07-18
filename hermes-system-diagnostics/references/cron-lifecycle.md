# Cron 任务生命周期与陷阱

## 调度格式

| 类型 | 格式 | 示例 |
|------|------|------|
| 循环 | `every <N><unit>` | `every 30m`, `every 2h` |
| Cron 表达式 | `分 时 日 月 周` | `0 9 * * *` (每天9点) |
| 一次性 ISO | ISO 时间戳 | `2026-07-20T09:00:00` |

❌ 不存在的格式：`once in 30m` → 应该用 `every 30m`

## One-shot 任务的生命周期

```
创建 → scheduled → running → completed (one-shot 完成即死)
                                    ↓
                            ❌ 不能 resume
```

One-shot cron 时间过了就不能 resume：
```
# 错误提示
"Cannot resume: one-shot time <ts> is in the past (grace window: 120s)"
```

**正确做法**：`cronjob remove` → `cronjob create` 重建。

## no_agent 任务

`no_agent=true` 的任务不经过 LLM：
- 只执行 `script` 参数指定的脚本
- 脚本 stdout 即为交付内容
- stdout 为空 = 静默，不通知用户
- 非零退出码 = 发送错误告警

适用场景：Watchdog、打卡脚本、简单轮询等。

## 本机已知任务（2026-07-16）

| ID | 名称 | 调度 | 状态 |
|----|------|------|------|
| `3dbb3c9` | Notion 每日快检 | 每天 9:00 | error |
| `6fa3f7a` | Notion 每周深度巡检 | 周一 9:00 | ok |
| `37c5912` | 万凯周报生成 | 周六 17:30 | 从未运行 |
| `eb72a40` | 万凯数据看板 | 周六 17:30 | 从未运行 |
| `0a54b41` | 下班前同步 | 每天 17:45 | error |
| `7e961a0` | 到家后同步 | 每天 18:30 | error |
| `3faa1d3` | AI会员监控 | 每2小时 | error |
| `18f6138` | AI会员·部署 | 每2小时 | error |
| `a697edd` | Watchdog | 每30分钟 | ok（脚本路径已修复） |
| `6a97548` | 午休打卡 | 每天 13:27 | 从未运行 |

## 常见 Error 排查

多数 `last_status=error` 的根因可能是：
1. Cron 执行时 `.env` 未正确加载（API key 缺失）
2. **脚本路径不正确** — 本机 `~/.hermes` ≠ `~/AppData/Local/hermes`（后者是 `E:\hermes` 的软链接）。`no_agent` cron 从数据目录解析脚本，修改脚本后必须同步到 `/e/hermes/scripts/`
3. Notion API 参数格式变更（v2025-09-03 的 `data_source` vs `database` 差异）
