---
name: notion-governance
description: "Notion knowledge-base governance: scan, classify, deduplicate, auto-fix, and cron-monitor a Notion workspace like a CI/CD pipeline."
version: 1.0.0
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_API_KEY]
---

# Notion Governance OS

Build a continuous governance system for a Notion workspace — scan for issues, auto-fix where possible, track everything in a dashboard, and run scheduled inspections via Hermes cron.

## When to Use

- User has a large Notion workspace (1000+ pages) that's gotten messy
- User wants automated inspection, not one-time cleanup
- User wants issue tracking in a dedicated Notion database
- User wants scheduled (cron) monitoring

## Core Principle: Auto-Fix Before Reporting

**用户只想看到干净结果。** 巡检发现可自动修复的问题（编码损坏标题、无标题页面）时，必须先自动修复再汇报，而不是把问题清单丢给用户。用户原话：*"以后可以直接做成无乱码的，我要直接看到好的结果"*。

所有 cron 任务和手动巡检都应遵循：scan → auto-fix → report clean results。

## Architecture

```
scanner.py → detects issues (untitled, garbled, duplicates, etc.)
dashboard.py → writes issues to a governance database
fixer.py → auto-repairs fixable issues (titles, archives)
cron jobs → daily quick scan + weekly deep scan
```

### POST-with-properties 400 Quirk

`POST /v1/pages` with database properties (select, multi_select, rich_text, relation, date) returns a confusing 400 requiring `id/name/start/lat/state` fields — a server-side validation quirk, **not** a client payload problem. The same payload that fails in POST works fine in PATCH.

**Fix — create-then-PATCH:**

```bash
# Step 1: Create page with ONLY the title
curl -s -X POST 'https://api.notion.com/v1/pages' \
  -H 'Authorization: Bearer '"$NOTION_API_KEY" \
  -H 'Notion-Version: 2025-09-03' \
  -H 'Content-Type: application/json' \
  -d '{
    "parent": {"database_id": "DB_ID"},
    "properties": {
      "title": [{"text": {"content": "Page Title"}}]
    }
  }'
# → returns page_id

# Step 2: PATCH the remaining properties onto the new page
curl -s -X PATCH "https://api.notion.com/v1/pages/PAGE_ID" \
  -H 'Authorization: Bearer '"$NOTION_API_KEY" \
  -H 'Notion-Version: 2025-09-03" \
  -H 'Content-Type: application/json' \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Done"}},
      "Notes": {"rich_text": [{"text": {"content": "..."}}]}
    }
  }'
```

> **Full procedure with more examples:** `references/api-pitfalls.md`

### 5. Batch Create Pages (Pattern)

When creating many pages at once (e.g., seeding a database from existing data), use Python `urllib.request` for control — not shell `curl` loops — to avoid Windows shell encoding issues with Chinese characters and special characters in passwords.

```python
import urllib.request, json, ssl, time, os

key = os.environ.get('NOTION_API_KEY', '')
DB_ID = "your-database-id"
HEADERS = {"Authorization": f"Bearer {key}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"}

def create_page(properties):
    data = json.dumps({"parent": {"database_id": DB_ID}, "properties": {"title": [{"text": {"content": properties.pop("title")}}]}}).encode('utf-8')
    req = urllib.request.Request("https://api.notion.com/v1/pages", data=data, method="POST", headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=30)
    page_id = json.loads(resp.read().decode())["id"]
    # PATCH remaining properties (to avoid POST-with-properties quirk)
    if properties:
        patch = json.dumps({"properties": properties}).encode('utf-8')
        urllib.request.urlopen(urllib.request.Request(f"https://api.notion.com/v1/pages/{page_id}", data=patch, method="PATCH", headers=HEADERS), timeout=30)
    return page_id
```

### 6. Formula: "第X周 M/D" Week+Date Display

To display week number alongside date in a formula property (Chinese format):

```json
{"formula": {"expression": "\"第\" + formatDate(prop(\"日期\"), \"w\") + \"周 \" + formatDate(prop(\"日期\"), \"M/D\")"}}
```

Render: `第29周 7/15`

## API Pitfalls: v2025-09-03

> **Full procedure with code samples:** `references/api-pitfalls.md`

### Creating Databases

`POST /v1/data_sources` does NOT work for creating databases with properties.

**Correct two-step process:**

1. **Create shell** via `POST /v1/databases`:
   - Parent MUST include `"type": "page_id"`: `{"type": "page_id", "page_id": "xxx"}`
   - Title entries need `"type": "text"` wrapper
   - Properties added in this call are silently ignored

2. **Add properties** via `PATCH /v1/data_sources/{data_source_id}`:
   - ⚠️ **CRITICAL: `data_source_id` ≠ `database_id` for new databases.** `POST /v1/databases` returns the `database_id` only. Using that on `/v1/data_sources/` → 404. Search first for the real `data_source_id`.

**Two distinct IDs per database — DO NOT confuse:**
- `database_id` — returned by `POST /v1/databases`. Use for page creation: `parent: {"database_id": "..."}`
- `data_source_id` — obtained via `POST /v1/search` (databases returned as `"object": "data_source"`). Use for queries (`/v1/data_sources/{ds_id}/query`) and property PATCH (`/v1/data_sources/{ds_id}`)

**Verified (2026-07-16):** Creating DB → `database_id: dd765009-...`. Search → `data_source_id: 64d2f1dd-...`. PATCHing `/v1/data_sources/{database_id}` → **404**. PATCHing `/v1/data_sources/{data_source_id}` → **200 OK**.

**Correct create+properties workflow:**
```bash
# 1. Create → get database_id
DB_ID=$(curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" -H "Content-Type: application/json" \
  -d '{"parent":{"type":"page_id","page_id":"PAGE_ID"},"title":[{"type":"text","text":{"content":"My DB"}}]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 2. Search → get real data_source_id
DS_ID=$(curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" -H "Content-Type: application/json" \
  -d '{"query":"My DB"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print([r['id'] for r in d['results'] if r.get('object')=='data_source'][0])")

# 3. PATCH properties with data_source_id
curl -s -X PATCH "https://api.notion.com/v1/data_sources/$DS_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" -H "Content-Type: application/json" \
  -d '{"properties": {...}}'
```

### CRITICAL: Select/Multi-select PATCH Replaces, Not Appends

When you PATCH a select or multi_select property with options, **the entire options array is replaced — NOT merged**. This **deletes all existing options** not included in your body.

```python
# ❌ WRONG — deletes all existing options except these two:
props = {"properties": {"状态": {"select": {"options": [
    {"name": "📝 未定稿", "color": "yellow"},
    {"name": "✅ 已定稿", "color": "green"}
]}}}}
```

**ALWAYS include ALL existing options with their original colors:**
```python
# ✅ CORRECT — merge new + existing options into one array:
props = {"properties": {"状态": {"select": {"options": [
    {"name": "📝 未定稿", "color": "yellow"},    # new
    {"name": "✅ 已定稿", "color": "green"},     # new
    {"name": "✅ 已完成", "color": "green"},      # existing
    {"name": "🔄 进行中", "color": "blue"},       # existing
    {"name": "⏳ 待跟进", "color": "yellow"},     # existing
    {"name": "❌ 取消", "color": "red"},          # existing
    {"name": "📅 计划", "color": "gray"}          # existing
]}}}}
```

**Before adding options, query current options first** and merge. You CANNOT change an existing option's color — the API rejects with `"Cannot update color of select with name: ..."`.

### Deleting a Property

Set the property to `null`:
```python
props = {"properties": {"耗时(h)": None}}  # deletes the property
```

## System Setup

### 1. Create Governance Database

Create under a parent page (e.g., "Hermes 数据中心") with these properties:

| Property | Type | Options |
|----------|------|---------|
| Name | Title | — |
| 问题类型 | Select | 无标题, 编码损坏, 标题重复, 命名不规范, 空数据库, 孤立页面, 其他 |
| 严重级别 | Select | 🔴 严重, 🟡 警告, 🟢 建议 |
| 状态 | Select | 待处理, 处理中, 已修复, 已忽略 |
| 关联页面ID | Rich text | — |
| 发现日期 | Date | — |
| 修复日期 | Date | — |
| 自动化 | Checkbox | — |
| 备注 | Rich text | — |

Save `database_id` to `~/.hermes/notion_gov_config.json`.

### 2. Deploy Scripts

Three Python scripts live in `~/.hermes/scripts/notion-governance/`:

- **scanner.py** — Full/incremental workspace scan. Detection rules for 7 issue types. Supports `--no-fetch` (use cache), `--incremental` (changed items only), `--summary-only`, `--output`.
- **dashboard.py** — Writes issues to governance DB with dedup. Supports `--dry-run`, `--limit`, `--offset`, `--only-critical`.
- **fixer.py** — Auto-repairs: infers titles from page content (H1 → first meaningful line → page reference), archives empty DBs. Supports `--dry-run`, `--type`, `--page-id`.

### 3. Schedule Cron Jobs

Three tiers:

| Job | Schedule | Mode |
|-----|----------|------|
| Daily quick scan | `0 9 * * *` | `--incremental`, report only |
| Weekly deep scan | `0 9 * * 1` | Full scan + write to DB + Chinese report |
| Monthly report | optional | Summary from governance DB |

## Detection Rules

| Rule | Severity | Auto-fixable |
|------|----------|--------------|
| Untitled pages | 🔴 | Yes (infer from H1) |
| Garbled titles (U+FFFD) | 🔴 | Yes (infer from H1) |
| Vague names (digits, "temp", single-char) | 🟡 | No |
| Exact duplicate titles (173+ groups) | 🟡 | No |
| Empty databases | 🟡 | Yes (archive) |
| Unnamed databases | 🔴 | No |
| Loose workspace pages | 🟡 | No |

## Fixer: Title Inference

When a page has no title or a garbled title, the fixer reads the page markdown and applies these strategies in order:

1. **First H1 heading** — `# Some Title` → strip markdown formatting
2. **First meaningful line** — first non-empty, non-tag line ≥10 chars
3. **Page reference** — `<page url="...">Title</page>` in content (common for linked pages)
4. **Callout text** — first `<callout>` content

Always `--dry-run` first to preview changes.

## Operations Playbook

### Full scan + write to DB
```bash
cd ~/.hermes/scripts/notion-governance
python scanner.py --output ~/.hermes/reports/scan_latest.json
python dashboard.py ~/.hermes/reports/scan_latest.json
```

### Incremental daily check
```bash
python scanner.py --incremental --summary-only
```

### Fix garbled titles (dry-run first)
```bash
python fixer.py ~/.hermes/reports/scan_latest.json --type 编码损坏 --dry-run
python fixer.py ~/.hermes/reports/scan_latest.json --type 编码损坏 --limit 5
```

### Batch write with offset (for large workspaces)
```bash
# Write issues 100-199
python dashboard.py scan.json --offset 100 --limit 100
```

## Rate Limiting

Notion API allows ~3 req/s average. The scripts use:
- Scanner: no artificial delay (reads are fast)
- Dashboard: 0.4s delay between writes (~2.5 req/s, safe margin)
- Fixer: 0.6s delay (~1.7 req/s, extra conservative)

**Real-world throughput** (measured 2026-07):
- Dashboard writes ~0.7 条/秒 including API overhead + dedup queries
- 822 issues took ~20 minutes (1,224 seconds)
- 5,937 items full scan: ~2 minutes API fetch + ~1 second analysis from cache
- Always use background terminal or cron for writes >100 issues
- The `--limit` flag alone gives the same first-N slice — always pair with `--offset` for batch processing

## Fixer Post-Review Protocol

After auto-fixing titles, manually review the ones that used fallback strategies:

1. **H1 extraction** (策略1) — usually correct, no review needed
2. **First-line fallback** (策略2) — often picks conversational sentences like "黄总，你的判断方向是对的..." or "我先用一下 brainstorming..." — **must review** and replace with a descriptive title based on the page's actual topic
3. **Page reference** (策略3) — usually correct
4. **Callout extraction** (策略4) — variable quality, review recommended

For truly empty pages (`<empty-block/>`), name them "空页面（待清理）" and flag for deletion later.

## Path Handling on Windows

Bash (`$HOME`) resolves to `/c/Users/<user>/` but Python sandbox can't read from that path. When passing paths between tools:
- Use `C:\Users\<user>\...` for Python/write_file tools
- Use `/c/Users/<user>/...` for bash/terminal commands
- 用中文输出

## Inbox → Weekly Tasks Linkage Pattern

When the user wants to "promote" items from a catch-all inbox database into an action-oriented tasks database, use this bidirectional Relation + Checkbox pattern.

### Database Setup

1. **Add a bidirectional Relation** on the inbox data source pointing to the tasks data source. See `references/relation-properties.md` for the exact v2025-09-03 API syntax — critical pitfalls: use `dual_property` (not `two_way_property`) and flat `data_source_id` (not nested inside `data_source`).

2. **Add a Checkbox `已转入`** on the inbox to track transfer status.

3. **Rename the auto-generated reverse property** — Notion produces verbose names like `"Related to 📥 DB_NAME (property_name)"`. PATCH the target data source to rename it to something clean like `"来自收件箱"`.

### Transfer Script

`scripts/inbox-to-task.py` handles batch promotion:

```bash
python scripts/inbox-to-task.py                    # transfer all unchecked items
python scripts/inbox-to-task.py --dry-run          # preview only
python scripts/inbox-to-task.py --id <page_id>     # single item
python scripts/inbox-to-task.py --priority "🔥 现在就做"  # filter by priority
```

The script maps Inbox fields to Task fields:
- `优先级` → `优先级` (with mapping: 🔥 现在就做→P0 紧急, ⚡ 本周→P1 高, 📌 本月→P2 正常, 💤 以后再说→P3 低)
- `类型` → `任务类别` (best-effort: 📌 待办→✅ 其他, 💡 想法→📈 计划总结, etc.)
- Sets `状态` to `📅 计划` and `日期` to today
- Appends `📥 从收件箱转入` to 备注 with original note preserved

Override DB IDs via env vars: `NOTION_INBOX_DS_ID`, `NOTION_WEEKLY_DB_ID`.

### Manual One-Click (Notion UI)

In the Notion app, open an inbox item → click the Relation property → "Search or create" → type to find an existing task or create a new one. Then check `已转入`. This is the simplest per-item workflow.

### Config

Store linkage config in `~/.hermes/wankai_inbox_config.json`:
```json
{
  "linked_to": {
    "weekly_db_id": "...",
    "relation_property": "关联事务",
    "reverse_property": "来自收件箱",
    "transfer_checkbox": "已转入"
  },
  "priority_map": { ... }
}
```

## Files

```
~/.hermes/
├── notion_gov_config.json          # governance DB IDs
├── notion_scan_cache.json          # full workspace snapshot
├── notion_gov_dedup.json           # written-issue fingerprints
├── wankai_weekly_config.json       # weekly log DB IDs (DingTalk example)
├── wankai_inbox_config.json        # inbox→weekly linkage config
├── scripts/notion-governance/
│   ├── scanner.py
│   ├── dashboard.py
│   └── fixer.py
├── scripts/notion-inbox-to-task.py # inbox transfer script (deployed copy)
└── reports/
    └── scan_latest.json
```

### Skill Support Files

- `references/relation-properties.md` — v2025-09-03 relation property creation with correct syntax and known failures
- `references/wankai-workspace.md` — 万凯工作台 workspace structure, database IDs, and property schemas
- `references/proactive-work-monitoring.md` — 主动工作滞留监控：判定标准、桌面联动、Watchdog + 钉钉通知 + 打卡自动化
- `references/brothers-collaboration.md` — Hermes 兄弟协作系统：消息板数据库、签名约定、每日签到协议、双 Hermes 互通
- `references/windows-toast-notifications.md` — Windows 原生通知集成
- `scripts/inbox-to-task.py` — batch transfer script (inbox → weekly tasks)

## Hermes Cross-Device Synchronization Pattern

When the user needs to synchronize Hermes data between company and home computers using Notion as the intermediary:

### Cross-Device Sync Architecture

```
公司电脑 (17:45) → Notion数据中心 → 家里电脑 (18:30)
       ↓                   ↓                   ↓
   自动同步           数据中介           自动恢复
   (sync_to_notion)   (Notion数据库)   (sync_from_notion)
```

### Implementation Components

Three core scripts live in `~/.hermes/scripts/hermes-sync/`:

- **create_sync_database.py** — Creates the Hermes sync management database in Notion with properties for tracking sync operations
- **sync_to_notion.py** — Executes on company computer at 17:45 daily to backup files, create snapshots, sync conversations, and update the Notion database
- **sync_from_notion.py** — Executes on home computer at 18:30 daily to restore files from snapshots and sync conversations

### Database Schema for Sync Management

Create under a parent page (e.g., "Hermes 数据中心" or "万凯工作台") with these properties:

| Property | Type | Options |
|----------|------|---------|
| 同步时间 | Created time | — |
| 同步类型 | Select | 📥公司→Notion, 📤Notion→家里, 🔄双向同步, 📁文件备份, 💬对话同步, ⚠️同步失败 |
| 设备 | Select | 公司电脑, 家里电脑, Notion数据中心 |
| 状态 | Select | ✅已完成, 🔄进行中, ⏳待处理, ❌失败 |
| 同步内容 | Rich text | — |
| 文件数量 | Number | — |
| 对话数量 | Number | — |
| 数据大小 | Number | Format: KB |
| 备注 | Rich text | — |

Save `sync_database_id` to `~/.hermes/hermes_sync_config.json`.

### Cron Jobs Setup

Two scheduled cron jobs (created via cronjob action='create'):

| Job | Schedule | Script | Purpose |
|-----|----------|--------|---------|
| 公司电脑下班前同步 | `45 17 * * 1-6` | sync_to_notion.py | Daily 5:45 PM backup before leaving work |
| 家里电脑到家后同步 | `30 18 * * *` | sync_from_notion.py | Daily 6:30 PM restore after arriving home |

### Sync Workflow: Company Computer → Notion

```bash
# 1. Backup important files
- .env configuration
- config.yaml configuration  
- hermes_sync_config.json
- 万凯包装_精简档案.md
- Other critical Hermes files

# 2. Create system snapshot
- Timestamped directory in ~/.hermes/sync_backups/
- Contains all backed up files
- Includes sync_info.json with metadata

# 3. Sync conversations
- Query recent conversations via session_search
- Upload to Notion sync database
- Record conversation count and size

# 4. Update Notion sync database
- Record sync time, file count, data size
- Mark sync type and status
- Generate sync report
```

### Sync Workflow: Notion → Home Computer

```bash
# 1. Restore files from latest snapshot
- Find latest snapshot in ~/.hermes/sync_backups/
- Copy files to local Hermes directories
- Verify file integrity

# 2. Sync conversations
- Query conversations from Notion sync database
- Save to local conversation history
- Ensure continuity of work

# 3. Update local sync status
- Record last sync time
- Mark sync completion
- Generate restore report
```

### File Structure

```
~/.hermes/
├── scripts/hermes-sync/
│   ├── create_sync_database.py
│   ├── sync_to_notion.py
│   ├── sync_from_notion.py
│   └── README.md
├── sync_backups/
│   ├── sync_snapshot_20260713_174500/
│   │   ├── .env
│   │   ├── config.yaml
│   │   ├── hermes_sync_config.json
│   │   └── sync_info.json
│   ├── sync_report_20260713_174500.json
│   └── sync_from_notion_report_20260713_183000.json
└── hermes_sync_config.json
```

### Error Handling and Best Practices

**Rate Limiting:** Notion API allows ~3 req/s. Scripts include delays between operations to stay within limits.

**Path Handling on Windows:** Use `C:\Users\<user>\...` for Python tools and `/c/Users/<user>/...` for bash commands due to MSYS path translation.

**Atomic Operations:** Each sync step should be atomic - either fully complete or fully rolled back on failure.

**State Tracking:** Record sync status after each step to enable recovery from failures.

**Backup Strategy:** Always create snapshots before modifying critical files.

### Operations Playbook

**Create sync database:**
```bash
python ~/.hermes/scripts/hermes-sync/create_sync_database.py
```

**Manual sync on company computer:**
```bash
python ~/.hermes/scripts/hermes-sync/sync_to_notion.py
```

**Manual restore on home computer:**
```bash
python ~/.hermes/scripts/hermes-sync/sync_from_notion.py
```

**View sync reports:**
```bash
ls -la ~/.hermes/sync_backups/sync_report_*.json
cat ~/.hermes/sync_status.json
```

### User Preferences Embedded

- **Automation first**: No manual forms or user input required during sync
- **Clean results**: Auto-fix issues before reporting, provide clean output
- **Visual grouping**: Use emoji and color coding to distinguish sync periods
- **Direct delivery**: Results delivered immediately without additional steps

### Pitfalls and Gotchas

**Notion API Integration:**
- Always use `POST /v1/databases` to create databases, not `POST /v1/data_sources`
- Properties added during database creation are silently ignored
- Use `PATCH /v1/data_sources/{id}` to add properties after creation

**Windows Path Issues:**
- Python tools expect Windows-style paths: `C:\Users\...`
- Bash commands expect MSYS-style paths: `/c/Users/...`
- The `$HOME` environment variable may not match in both contexts

**Sync Timing:**
- Company computer sync at 17:45 (30 minutes before typical end of work)
- Home computer sync at 18:30 (30 minutes after typical arrival home)
- Avoid syncing during peak work hours to prevent interference

**Error Recovery:**
- If Notion API fails, scripts should save local snapshots as fallback
- Always `--dry-run` first when testing new sync configurations
- Provide clear error messages with actionable next steps

### Integration with Existing Notion Governance

This cross-device sync pattern integrates seamlessly with existing Notion governance:

- Uses the same Notion API key and authentication
- Stores sync data in dedicated databases under the governance workspace
- Follows the same auto-fix-before-report pattern
- Can be monitored via existing cron jobs and dashboards

### Future Enhancements

- Add GitHub repository synchronization
- Implement incremental file sync to reduce bandwidth
- Add conflict resolution for concurrent edits
- Support multiple Hermes profiles across devices
- Add encryption for sensitive data sync

## Hermes Brothers Collaboration Pattern

When the user runs two Hermes instances (company + home) that need to coordinate through Notion:

### Concept

Two Hermes agents share a Notion message board database to exchange messages, check-in daily, and coordinate tasks. Each Hermes knows its identity via `~/.hermes/hermes_identity.json` and follows a shared protocol.

### Core Rules

1. **Signature convention** — append `📝 由 [🏢/🏠 Hermes·X] 记录 · timestamp CST` to every Notion write
2. **Daily check-in** — on first interaction each day, query the message board for brother's messages
3. **Message types** — 👋签到 / 📢公告 / 💬留言 / 📋任务 / 🔄同步 / ⚠️警告 / 📝笔记
4. **Priority levels** — 🔥紧急(immediate) / ⚡重要(24h) / 📌普通(when free) / 💤低(no reply needed)

### Database Setup

Create under the "Hermes 数据中心" parent page using create-then-PATCH with corrected data_source_id (not database_id — see API pitfalls above).

Full protocol and schema in `references/brothers-collaboration.md`.

## DingTalk Weekly Report Pattern

When the user needs to generate weekly work reports from a Notion daily log:

### Daily Log Database Schema

Create under the work hub page (e.g., "万凯工作台") with properties tailored to the user's actual work patterns. **Study the user's existing daily log first** to derive the right categories.

**Optimized schema (based on 两个月 of real work data analysis):**

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Task description |
| 日期 | Date | When the work was done |
| 任务类别 | Select | 🎨电商设计 / 🖌️客户LOGO / 📦产品物料 / 📱小程序 / 📊平台巡查 / 📰每日资讯 / 💻内部事务 / 📞沟通协作 / 🔍竞品监控 / 📈计划总结 / ✅其他 |
| 状态 | Select | 📝未定稿 → ✅已定稿 (设计流) | 🔄进行中 → ✅已完成 (通用流) | ⏳待跟进 / ❌取消 / 📅计划 |
| 优先级 | Select | 🔥P0紧急 / ⚡P1高 / 📌P2正常 / 💤P3低 |
| 平台 | Multi-select | 淘宝 / 拼多多 / 抖店 / 小程序 / 官网 / 1688 / 公众号 |
| 客户 | Rich text | Client name the task was for |
| 瓶型 | Multi-select | 330A / 330B / 500A / 500B / 500C / 700A / 迷你款 / 自动款 / 升降款 |
| 备注 | Rich text | Extra notes or context |

**Status flow design:**
```
📅 计划 ──→ 🔄 进行中 ──→ ✅ 已完成       (通用工作流)
                │
                └──→ ⏳ 待跟进              (被阻塞)

📅 计划 ──→ 🔄 进行中 ──→ 📝 未定稿 ──→ ✅ 已定稿  (客户设计流)
```

**Do NOT include a 耗时(h) property** — users find it friction. The 备注 field covers the same need.

### Cron Job

```yaml
schedule: "30 17 * * 6"  # Saturday 5:30 PM — half hour before下班
```

### Report Output: Write to Notion, Not Just Text

The cron job should **create a new Notion page** under the work hub with the formatted report, not just output text. This gives permanent archive + searchability.

**Page creation approach:**
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "<work_hub_page_id>"},
    "properties": {
      "title": [{"text": {"content": "📊 周报 · W29 · 07.13-07.18"}}]
    },
    "children": [...blocks...]
  }'
```

**Page title format:** `📊 周报 · W{ISO week number} · {Mon date}-{Sat date}`

**Content:** Use Notion blocks (heading_2, paragraph, bulleted_list_item, table) NOT just markdown text. Include a brief stats summary at the top.

### Cron Prompt Structure

The cron prompt must be self-contained with explicit API calls:

1. **Query the data source** for this week's entries (Monday–Saturday)
   ```bash
   curl -s -X POST "https://api.notion.com/v1/data_sources/{DS_ID}/query" \
     -H "Authorization: Bearer $NOTION_API_KEY" \
     -H "Notion-Version: 2025-09-03" \
     -d '{"page_size": 100, "sorts": [{"property": "日期", "direction": "ascending"}]}'
   ```
2. **Filter** for current week's entries by date
3. **Categorize** by type and status
4. **Generate** report in the exact format the user's company requires

### Standard DingTalk Report Template

```
【本周工作内容】
按类别分组，每条一行

【本周未完成工作】
进度 + 原因 + 预计完成节点

【本周工作总结】
学到了什么、感悟、失误、改进

【下周工作计划目标】
量化目标 + 时间节点

【需协调与帮助】
遇到的问题

【意见和反馈】
对公司/团队的意见
```

### Key Rules for Report Generation

- 只上报工作相关内容，过滤掉无关紧要的思考和小备忘
- 语言正式但自然，像真人在写周报
- 如果本周数据库为空，如实说明并建议补录
- 下周工作计划从本周未完成项推测
- 用中文输出
