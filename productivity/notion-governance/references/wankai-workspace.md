# 万凯工作台 — Notion Workspace Reference

> Created: 2026-07-15 | User: 万凯包装(NEZE) 美工设计岗

## Workspace Structure

```
万凯工作台 (page: b3fcfcd9-c2b3-4515-a81c-5718846d0cb6)
├── 📋 每周事务 · Weekly Log (DB)
├── 📥 万凯收件箱 (DB)
├── 📊 周报 (page)
├── 🔮 AI洞察 (page)
├── 📈 数据看板 (page)
├── 📌 工作要点库 (DB) ← 2026-07-15 新增
├── 🔑 账号密码管理 (DB) ← 2026-07-15 新增
└── 🛡️ 治理面板 (DB, governance)
```

## Database IDs

| Database | database_id | data_source_id | Purpose |
|----------|-------------|----------------|---------|
| 每周事务 · Weekly Log | 97eba705-25a9-40d6-98ec-db082d171e26 | 139e8c07-a5f0-4537-87f7-73c4ba691f67 | 日常工作记录 |
| 万凯收件箱 | 4a99dd71-fa65-4b2c-8675-dc3fea33da32 | 58324c59-26fe-4c52-8809-7cfccf707b74 | 想法/待办收集 |
| 📌 工作要点库 | 5b0a04b2-bea5-40ce-978a-0da82965dc6d | 5c94fd12-95b3-4e82-8c5e-b9eafc17f86e | 注意事项/规范手册 |
| 🔑 账号密码管理 | ff0bac61-ccc0-4c76-a045-54f38d567073 | 8620721f-544d-47b9-a90e-c360c50e4d05 | 店铺账号密码 |
| 🛡️ 治理面板 | 02d80532-c500-486c-92e1-ec374f51b06c | (governance DB) | 知识库治理 |

## 每周事务 — Key Properties

| Property | Type | Notes |
|----------|------|-------|
| Name | Title | Task description |
| 日期 | Date | Work date |
| 周次 | Formula | `第X周 M/D` format (auto from 日期) |
| 任务类别 | Select | 🎨电商设计 / 🖌️客户LOGO / 📦产品物料 / 📱小程序 / 📊平台巡查 / 📰每日资讯 / 💻内部事务 / 📞沟通协作 / 🔍竞品监控 / 📈计划总结 / ✅其他 |
| 状态 | Select | 📝未定稿 / ✅已定稿 / ✅已完成 / 🔄进行中 / ⏳待跟进 / ❌取消 / 📅计划 |
| 优先级 | Select | 🔥P0紧急 / ⚡P1高 / 📌P2正常 / 💤P3低 |
| 平台 | Multi-select | 淘宝 / 拼多多 / 抖店 / 小程序 / 官网 / 1688 / 公众号 |
| 客户 | Rich text | Client name |
| 瓶型 | Multi-select | 330A / 330B / 500A / 500B / 500C / 700A / 迷你款 / 自动款 / 升降款 |
| 备注 | Rich text | Extra context |

## 📌 工作要点库 — Key Properties

| Property | Type | Options |
|----------|------|---------|
| Name | Title | 要点标题 |
| 类别 | Select | 🎨设计技巧 / 🙋客户需求 / 📏平台规则 / 🖨️印刷物料 / 🔧软件操作 / 📋内部流程 / ⚠️易错提醒 / 💡其他 |
| 优先级 | Select | 🔴核心要点 / 🟡重要提醒 / 🟢一般参考 |
| 适用场景 | Multi-select | 淘宝主图 / 拼多多主图 / 抖店主图 / 详情页 / LOGO效果图 / 产品物料 / 说明书 / 纸箱 / CE证书 / 每日资讯海报 / 平台巡查 |
| 状态 | Select | ✅生效中 / 📝草稿 / ⚠️待确认 / ❌已过时 |
| 关键词标签 | Multi-select | 尺寸规范 / 色彩模式 / 文字要求 / 出血位 / 分辨率 / 客户偏好 / 修改频率 |
| 关联事务 | Relation | ↔ 每周事务 (双向) |
| 备注 | Rich text | 补充说明 |

## 🔑 账号密码管理 — Key Properties

| Property | Type | Options |
|----------|------|---------|
| Name | Title | 账号名称 |
| 平台/店铺名 | Select | 淘宝 / 拼多多 / 抖店 / 1688 / 官网 / 公众号 / 小程序 / 其他 |
| 账号 | Rich text | Login ID |
| 密码 | Rich text | Password |
| 绑定手机号 | Rich text | Linked phone |
| 绑定邮箱 | Rich text | Linked email |
| 密保问题 | Rich text | Security Q&A |
| 有效期 | Date | Expiry date |
| 状态 | Select | ✅正常 / ⚠️待验证 / ⏰即将过期 / ❌已过期 / 🚫已停用 |
| 备注 | Rich text | Notes |

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| 每日快速巡检 | `0 9 * * *` | Incremental scan + auto-fix |
| 每周深度巡检 | `0 9 * * 1` | Full scan + fix + report |
| 周六周报生成 | `30 17 * * 6` | Auto-generate DingTalk weekly report |
| 数据看板更新 | (existing) | Dashboard charts |

## Notes

- Notion API Version: `2025-09-03`
- API Key stored in: `C:\Users\win10\.hermes\.env` (NOTION_API_KEY)
- Integration shared with all databases under 万凯工作台
- Rate limit: ~3 req/s (use 0.5s delay for batch writes)
