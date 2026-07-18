# DingTalk Weekly Log Schema (Optimized)

> Updated 2026-07-13 — replaces the generic `类别`/`耗时(h)` schema with a domain-specific schema based on real work pattern analysis.

## Design Principle

Analyze the user's existing daily task journal first — discover their real categories, platforms, product lines, and workflow patterns. Design the schema around those patterns, not generic fields.

## Optimized Schema (万凯包装 example)

| Property | Type | Options |
|----------|------|---------|
| Name | Title | Task description |
| 日期 | Date | When the work was done |
| 任务类别 | Select | 🎨电商设计 / 🖌️客户LOGO / 📦产品物料 / 📱小程序 / 📊平台巡查 / 📰每日资讯 / 💻内部事务 / 📞沟通协作 / 🔍竞品监控 / 📈计划总结 / ✅其他 |
| 状态 | Select | ✅已完成 / 🔄进行中 / ⏳待跟进 / ❌取消 / 📅计划 |
| 优先级 | Select | 🔥P0紧急 / ⚡P1高 / 📌P2正常 / 💤P3低 |
| 平台 | Multi-select | 淘宝 / 拼多多 / 抖店 / 小程序 / 官网 / 1688 / 公众号 / 其他平台 |
| 客户 | Rich text | Client name for LOGO rendering tasks |
| 瓶型 | Multi-select | Product SKU codes (330A, 迷你款, 自动款, etc.) |
| 备注 | Rich text | Extra notes, decisions, reminders |

## Anti-Patterns

- **`耗时(h)`** — users rarely fill in time estimates. Remove it.
- **`类别` (generic)** — use `任务类别` with domain-specific options instead.
- **Duplicates** — when upgrading schemas, old properties (e.g. `类别`) may persist alongside new ones (`任务类别`). Delete the old via `PATCH /v1/data_sources/{id}` with `{"properties": {"类别": null}}`.

## API Notes

- Create database shell: `POST /v1/databases` (NOT `/v1/data_sources`)
- Add properties: `PATCH /v1/data_sources/{id}`
- Delete properties: set to `null` on PATCH
- Valid select colors: `default, gray, brown, orange, yellow, green, blue, purple, pink, red` — NOT `teal`
