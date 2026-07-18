# Notion API v2025-09-03 Pitfalls

## Database Creation: Two-Step Required

The `POST /v1/data_sources` endpoint in v2025-09-03 does NOT support creating
databases with properties. It returns:
```
"Creating new databases with data sources is not supported in this endpoint
for API version 2025-09-03 and later. Use the Create Database API instead."
```

### Step 1: Create the database shell

```bash
curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "PARENT_PAGE_UUID"},
    "is_inline": false,
    "title": [{"type": "text", "text": {"content": "DB Name"}}],
    "properties": {
      "Name": {"title": {}}
    }
  }'
```

Key: `parent` MUST include `"type": "page_id"` wrapper.
`title` entries need `"type": "text"` wrapper.
Properties added here are **silently ignored** — only `"Name": {"title": {}}` survives.

### Step 2: Get the real data_source_id, then add properties via PATCH

⚠️ The `id` returned in Step 1 is the `database_id`. The `data_source_id` may be
**different** (see "Two IDs Per Database" above). Search for the database first:

```bash
# Get the real data_source_id
DS_ID=$(curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "DB Name"}' | \
  python -c "import sys,json; d=json.load(sys.stdin); \
    print([r['id'] for r in d['results'] if r.get('object')=='data_source'][0])")

# Now PATCH with the real data_source_id
curl -s -X PATCH "https://api.notion.com/v1/data_sources/$DS_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {
        "select": {
          "options": [
            {"name": "Todo", "color": "red"},
            {"name": "Done", "color": "green"}
          ]
        }
      },
      "Date": {"date": {}}
    }
  }'
```

### Two IDs Per Database (⚠️ CRITICAL: They Can Differ)

- `database_id` — returned by `POST /v1/databases`. Use in `parent: {"database_id": "..."}` when creating pages.
- `data_source_id` — use in `POST /v1/data_sources/{id}/query` for queries AND `PATCH /v1/data_sources/{id}` for adding properties.
- Search results return databases as `"object": "data_source"`. The `data_source_id` field may be `null` — fall back to the `id` field.

**⚠️ database_id ≠ data_source_id in practice.** In a real-world case (2026-07-16):
- `POST /v1/databases` returned `database_id: dd765009-a30e-4dd4-a354-a77351ba6e7b`
- Searching for the same database returned `data_source_id: 64d2f1dd-255e-4bcb-bbe1-d5f127074501`
- These are **completely different UUIDs**. Using `database_id` for `PATCH /v1/data_sources/{id}` returns:
  ```
  HTTP 404: "Could not find data_source with ID: dd765009-..."
  ```

**Rule: After creating a database, ALWAYS search for it to get the real `data_source_id` before PATCHing properties or querying.** Never assume the database_id doubles as the data_source_id.

```bash
# Get the real data_source_id after creation:
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "YOUR DB NAME"}' | \
  python -c "import sys,json; d=json.load(sys.stdin); \
    print([r['id'] for r in d['results'] if r.get('object')=='data_source'][0])"
```

### Page Title Update

To fix a page title (e.g. garbled/empty):

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{PAGE_ID}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"title": [{"text": {"content": "New Title"}}]}}'
```

For database entries, find the title property name first (it may not be "title" — could be "Name", "日期标题", etc.), then use that key.

### Workspace-Level Database Creation

Cannot create a database directly at workspace level. Must specify a `parent.page_id`.
Choose a suitable parent page (e.g. "Hermes 数据中心").

### Title Inference from Content

When fixing untitled/garbled pages, read markdown first:
```bash
curl -s "https://api.notion.com/v1/pages/{PAGE_ID}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Inference priority:
1. First `# H1 heading` in markdown
2. First non-empty, non-tag line ≥10 chars
3. `<page url="...">Title</page>` reference in content
4. First `<callout>` text

### Rate Limiting

- Notion allows ~3 req/s average
- Write operations (PATCH/POST) are slower than reads
- Observed safe rates: 0.7 req/s for sustained writes (822 issues in 1224s)
- For bulk operations (1000+ items), use background processes or cron

### Cannot Create Duplicate Title Property

When PATCHing properties to a data_source, including a second `title` type property
alongside the default `Name` (which is already a title) returns:

```
"Cannot create new title property."
```

**Fix:** Use the existing `Name` property as the title field. Do not attempt to
add another title-typed property. The default `Name` is always present on new
databases.

### Database Properties Are Null on /v1/databases

In v2025-09-03, `GET /v1/databases/{database_id}` returns `"properties": null` (even after
properties are added). To read or verify properties, always use
`GET /v1/data_sources/{data_source_id}` instead — but note that `database_id` and
`data_source_id` may be **different UUIDs** (see "Two IDs" section above).
Search for the database first to get the real `data_source_id`, then query the
data_sources endpoint.

### JSON Control Characters in Large Responses

Notion API responses may contain control characters that cause `json.loads()` to fail
with `JSONDecodeError: Invalid control character`. 

**Fix:** Pipe large responses to file first (`-o /tmp/result.json`), then read and
parse. Or use `json.loads(text, strict=False)` / `json_parse()`.

### POST /v1/pages With Properties Returns 400 — Use Create-Then-PATCH

When creating a page inside a database with properties in a single `POST /v1/pages`
call, v2025-09-03 may return a confusing validation error asking for fields that don't
belong on the property type — for example, a `select` property produces:

```
body.properties.<name>.id should be defined, instead was `undefined`.
body.properties.<name>.name should be defined, instead was `undefined`.
body.properties.<name>.start should be defined, instead was `undefined`.
body.properties.<name>.lat should be defined, instead was `undefined`.
body.properties.<name>.state should be defined, instead was `undefined`.
```

This happens on **all property types** (select, multi_select, rich_text, relation, date)
and is a server-side validation quirk, not a client payload problem. The same payload
that fails in POST works fine in PATCH.

**Workaround — two-step create:**

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
  -H 'Notion-Version: 2025-09-03' \
  -H 'Content-Type: application/json' \
  -d '{
    "properties": {
      "类别": {"select": {"name": "📏 平台规则"}},
      "优先级": {"select": {"name": "🔴 核心要点"}},
      "适用场景": {"multi_select": [{"name": "淘宝主图"}]},
      "状态": {"select": {"name": "✅ 生效中"}},
      "备注": {"rich_text": [{"text": {"content": "..."}}]}
    }
  }'
```

**When this matters:** Any script or agent flow that creates database entries with
filled-in properties. If you see the `id/name/start/lat/state` error, switch to the
two-step pattern — do not try to satisfy the validation by adding those fields; they
are not valid on select/rich_text/etc. and will be rejected.
