# Hermes Watchdog 巡检脚本

## 架构

Cron 定时任务，`no_agent=true`，每 30 分钟运行一次。脚本静默执行，只有发现问题时才输出并推送通知。

- **脚本位置**: `~/.hermes/scripts/hermes_watchdog.py`（源） + `/e/hermes/scripts/hermes_watchdog.py`（cron 解析目标）
- **Cron job_id**: `a697edddb930`
- **通知渠道**: Windows Popup（`Wscript.Shell.Popup`，5 秒自动消失）+ 钉钉机器人 markdown

## 巡检模块

| 模块 | 检查内容 | 阈值 |
|------|---------|------|
| 🖥️ 桌面 | 散落设计文件 (>10个) / 大文件 (>100MB) / 残留下载 (>7天) | — |
| 💾 系统 | C盘空间 (/ 跨设备同步 (>3天) | 85%→警告, 90%→紧急 |
| 🔌 Notion | 错误缓存检查 | 上次 API 报错 |
| ⏰ 滞留任务 | 「🔄 进行中」>3天 / 「📅 计划」>5天 | — |

## ⚠️ 路径解析陷阱

**本机 `~/.hermes` ≠ `~/AppData/Local/hermes`**：后者是 `E:\hermes` 的软链接。

当 cron 用 `no_agent=true` + `script="hermes_watchdog.py"` 时，脚本从 **Hermes 数据目录**（即 `~/AppData/Local/hermes/scripts/` → `/e/hermes/scripts/`）解析，而非 `~/.hermes/scripts/`。

**修复方式**：修改脚本后必须同步到 `/e/hermes/scripts/`：
```bash
cp ~/.hermes/scripts/hermes_watchdog.py /e/hermes/scripts/hermes_watchdog.py
```

此规则适用于所有 `no_agent` 类型的 cron 脚本。

## 通知可靠性

| 旧方案 | 问题 | 新方案 |
|--------|------|--------|
| `Windows.UI.Notifications.ToastNotificationManager` | 需 AppUserModelID/开始菜单快捷方式，脚本环境下无此上下文 → 静默失败 | `Wscript.Shell.Popup` — 弹窗 5 秒自动消失，无需注册 |
| 钉钉 webhook | 正常 | 保持不变 |

## 错误缓存机制

- `check_stalled_tasks` 失败时写 `~/.hermes/.notion_last_error`，用于 `check_notion_connectivity` 告警
- 下次成功时自动清除缓存（`_clear_error_cache`）
- 按异常类型区分：`HTTPError`（含状态码+响应体）vs `URLError/OSError`（网络层）

## Datasource ID

每周事务数据库: `139e8c07-a5f0-4537-87f7-73c4ba691f67`（与 `wankai_dashboard.py` 一致）
