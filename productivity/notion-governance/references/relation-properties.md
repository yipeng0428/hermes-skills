# Notion v2025-09-03 Relation Properties

## Creating a Relation Between Two Data Sources

PATCH the source data source to add a relation property. The API uses field names that differ from what you'd expect:

### ✅ Correct syntax

```bash
curl -s -X PATCH "https://api.notion.com/v1/data_sources/{source_ds_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "关联事务": {
        "relation": {
          "data_source_id": "{target_ds_id}",
          "dual_property": {
            "name": "来自收件箱"
          }
        }
      }
    }
  }'
```

### ❌ Tried and failed

| Wrong attempt | Error message |
|---|---|
| `"two_way_property": {...}` | `single_property or dual_property should be defined` |
| `"data_source": {"data_source_id": "..."}` | `data_source_id should be defined, instead was undefined` |

### Key facts

- Use **`dual_property`** (not `two_way_property`) for bidirectional relations
- Use **`single_property`** (with empty object `{}`) for one-way relations
- Pass `data_source_id` as a **flat field** directly under `relation`, NOT nested inside a `data_source` wrapper
- The reverse property name is set in `dual_property.name` — this appears on the target database
- Notion auto-generates a verbose name like `"Related to 📥 DB_NAME (property_name)"` if you don't set `dual_property.name`

### Renaming the auto-generated reverse property

If the reverse name came out wrong, PATCH the target data source with the property's current name:

```bash
curl -s -X PATCH "https://api.notion.com/v1/data_sources/{target_ds_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "properties": {
      "Related to 📥 万凯收件箱 (关联事务)": {
        "name": "来自收件箱"
      }
    }
  }'
```

### Setting relation on a page

When creating or updating a page, the `relation` type takes an array of page IDs:

```json
{"关联事务": {"relation": [{"id": "target_page_id"}]}}
```

### Checking if a relation exists

Read the data source and look for `type: "relation"` in properties. The `relation` object contains `data_source_id` pointing to the linked database.
