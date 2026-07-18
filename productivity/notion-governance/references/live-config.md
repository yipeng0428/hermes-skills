# Cron Jobs — Production IDs

These are the live cron job IDs for the Notion governance system. Use these when managing (pause/resume/remove/update) jobs.

| Job | ID | Schedule | Mode |
|-----|-----|----------|------|
| Notion 每日快检 | `3dbb3c951f5c` | `0 9 * * *` | Incremental scan → auto-fix → report |
| Notion 每周深度巡检 | `6fa3f7afb10f` | `0 9 * * 1` | Full scan → auto-fix garbled → auto-fix untitled → write DB → weekly report |

## Governance Database

- **Name:** `🛡️ 治理面板 · Governance Dashboard`
- **database_id:** `02d80532-c500-486c-92e1-ec374f51b06c` (use for creating pages)
- **data_source_id:** `9005166f-b0f6-40e2-9336-2f1d00755840` (use for queries)
- **Parent:** `Hermes 数据中心` (`39b86cdd-9a32-81bd-a252-c45cf86c4924`)
- **Location:** `C:\Users\win10\.hermes\notion_gov_config.json`

## Workspace Stats (2026-07-13 baseline)

- Total items: 5,937 (5,667 pages + 270 databases)
- Issues detected: 1,062 (306 critical, 756 warnings)
- **Garbled titles: 11/11 fixed** ✅ (auto-inferred from content + 8 manually corrected)
- **Untitled standalone pages: 8/8 fixed** ✅ (auto-inferred + manually corrected)
- Remaining untitled: 287 (database entries with empty Name fields — needs per-DB schema handling)
- Pages in databases: 3,920 (69%)
- Top-level loose pages: 116
- Governance DB entries: 1,062 (full population)

## Performance Notes

- Full scan (5,937 items): ~2 minutes for API fetch
- Write to DB (1,000 issues): ~20 minutes at 0.7 req/s safe rate
- Fixer per-issue: ~2-3 seconds (reads page markdown + patches title)

## DingTalk Weekly Report (万凯)

- **Database:** `📋 每周事务 · Weekly Log`
- **database_id:** `97eba705-25a9-40d6-98ec-db082d171e26`
- **data_source_id:** `139e8c07-a5f0-4537-87f7-73c4ba691f67`
- **Parent:** `万凯工作台` (`b3fcfcd9-c2b3-4515-a81c-5718846d0cb6`)
- **Cron Job:** `37c5912b01ff` — `30 17 * * 6` (Saturday 5:30 PM)
- **Config:** `C:\Users\win10\.hermes\wankai_weekly_config.json`
- **Daily log schema:** Name (title), 日期 (date), 类别 (select: 设计制作/客户沟通/小程序/内部事务/竞品监控/学习研究/其他), 状态 (select: ✅已完成/🔄进行中/⏳待跟进/❌取消), 耗时(h) (number)
