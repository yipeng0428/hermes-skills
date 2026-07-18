# Notion Data Source ID Quirk

## Symptom

When querying a Notion database, a perfectly valid filter returns HTTP 400
("Bad Request") with no helpful error message. Direct queries without filters
work fine.

## Root Cause

When a database has a **relation property** pointing to another database,
Notion's `/search` endpoint may return **two** `data_source` entries for the
same database:

| Entry | Title | data_source_id | Behavior |
|-------|-------|---------------|----------|
| Main | "万凯收件箱" | `39e86cdd-9a32-80c8-b815-000b8b59320f` | 400 on filtered query |
| Relation shadow | (empty title) | `58324c59-26fe-4c52-8809-7cfccf707b74` | Works correctly |

Both share the same `database_id` (`4a99dd71-fa65-4b2c-8675-dc3fea33da32`).

The "relation shadow" entry has an empty `title` array but lists the related
database in its `description` field as a mention.

## Reproduction

```bash
# Search for the database
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query":"收件箱","filter":{"property":"object","value":"data_source"}}'

# Returns TWO results with different data_source_ids but same database_id
```

## Fix

When you get a 400 on a query that should work:

1. Check if `/search` returns multiple data_source entries for the same database
2. Try each `data_source_id` — one may work where the other doesn't
3. Prefer the entry that actually returns results on an unfiltered query

```python
# In your backend, test both
for ds_id in candidate_data_source_ids:
    resp = notion_post(f"/v1/data_sources/{ds_id}/query", {"page_size": 1})
    if resp.ok:
        DS_ID = ds_id  # use this one
        break
```

## Verified Environment

- Notion API version: 2025-09-03
- Database: 万凯收件箱 (Inbox with relation to 每周事务)
- Date: 2026-07-17
