---
name: hermes-system-diagnostics
description: Hermes 系统自检与诊断——每日签到、兄弟消息、cron健康、磁盘空间、连通性验证的完整流程。触发词：自检、系统检查、一切正常吗、诊断、health check。
category: hermes-setup
---

# Hermes 系统自检与诊断

完整的 Hermes Agent 系统健康检查流程。每次执行应覆盖五大模块。

## 触发条件

用户说「自检」「系统检查」「一切正常吗」「诊断」「health check」等。

## 自检五大模块

### 1. 每日签到
```bash
# 读取签到日期
cat ~/.hermes/.last_checkin_date
```
- 若非今日日期 → 需要签到（但当前会话即为签到，更新日期即可）
- 若为今日 → 已签到 ✅

### 2. 兄弟消息板
```bash
cd ~/.hermes && python scripts/hermes_brothers_check.py
```
- ⚠️ 注意：必须从 `~/.hermes` 目录运行，否则相对路径解析失败
- 检查是否有未读紧急消息（🔥 紧急 / ⚡ 重要）

### 3. Cron 任务健康
```
cronjob(action='list')
```
关注指标：
- `last_status`: error 的需要排查
- `enabled`: false 的已被禁用
- `next_run_at`: 确认调度正常
- `last_run_at`: null 表示从未运行

Watchdog 巡检详情见 `references/watchdog.md`。

### 4. 磁盘空间
Windows 上 MSYS `du` 对超大目录极慢（Windows/、WinSxS/、AppData/ 等），**不要用 du 递归扫描**。

正确做法：
```bash
# 用 PowerShell 脚本文件（不要 inline——管道变量 $_ 会被 bash 转义破坏）
# 1. 先写 .ps1 文件
# 2. 再执行: powershell -ExecutionPolicy Bypass -File "path/to/script.ps1"
```

快速检查：
```bash
df -h /c/                          # 整体使用率
ls -lh /c/pagefile.sys /c/hiberfil.sys /c/swapfile.sys  # 系统隐藏文件
```

更多技术细节见 `references/disk-scanning-windows.md`。

### 5. 基础连通性
```bash
# Notion API
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $(cat ~/.hermes/.notion_api_key)" \
  -H "Notion-Version: 2025-09-03" \
  "https://api.notion.com/v1/users/me"

# VPN 代理
curl -s -o /dev/null -w "%{proxy_code}" \
  --proxy 127.0.0.1:10793 --connect-timeout 5 \
  https://api.openai.com/v1/models

# Puppeteer Chrome
ls ~/.cache/puppeteer/chrome/win64-*/chrome-win64/chrome.exe
```

## 常见问题速查

| 问题 | 原因 | 修复 |
|------|------|------|
| Watchdog disabled | 旧 one-shot 过期 | `cronjob remove` + `create` 重建 |
| `last_status=error` | 可能 API key 未加载 | 检查 cron 执行时 .env 是否生效 |
| 兄弟脚本报路径错 | 不在 hermes 目录运行 | `cd ~/.hermes` 再执行 |
| PowerShell 脚本解析错 | inline 时 `$_` 被 bash 转义 | 写 .ps1 文件再执行 |
| no_agent cron 报 error | 脚本不在数据目录 | 本机 `~/.hermes` ≠ `~/AppData/Local/hermes`（→`/e/hermes`），修改后需同步 |

## Cron 管理陷阱

参见 `references/cron-lifecycle.md`。

### 快速参考
- 循环任务：`every 30m`、`every 2h`（不是 `once in 30m`）
- One-shot 过期后**不能 resume**——必须 delete + create
- `no_agent=true` 的任务靠 `script` 参数执行，不经过 LLM

## 清理操作

```bash
# Hermes 自身临时文件（安全删除）
rm -f ~/.hermes/tmp_*.json
rm -rf ~/.hermes/tmp_notion/
```
