# Notion API v2025-09-03 关键行为与踩坑记录

> 基于实际开发 Notion 治理系统总结。此版本与旧版 API（v2022-06-28）差异较大。

---

## 1. 数据库创建：两步法

### 旧版（v2022-06-28）：一步到位
```
POST /v1/databases → 返回带 properties 的完整对象
```

### 新版（v2025-09-03）：两步完成
```
Step 1: POST /v1/databases → 创建数据库骨架（properties 为 null 或不完整）
Step 2: PATCH /v1/data_sources/{data_source_id} → 添加自定义属性
```

**为什么？** 新版把"数据库定义"和"属性定义"拆成了两个独立对象：
- `database_id` — 用于创建页面（POST /v1/pages）
- `data_source_id` — 用于查询和修改属性（POST query / PATCH properties）

获取 data_source_id 的方式：
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -d '{"query": "数据库名称"}' | jq '.results[] | select(.object=="data_source") | .id'
```

---

## 2. Select/Multi-Select 属性操作

### ⚠️ 致命陷阱：PATCH 会 REPLACE 而非 APPEND

```bash
# 假设现有选项: ["✅ 已完成", "🔄 进行中", "⏳ 待跟进"]

# ❌ 错误：只传新选项 → 旧选项全部被删除！
PATCH /v1/data_sources/{id}
{
  "properties": {
    "状态": {
      "select": {
        "options": [
          {"name": "📝 未定稿", "color": "yellow"}   # ← 新选项
        ]
      }
    }
  }
}
# 结果: options = ["📝 未定稿"]  ← 旧的全部丢失！

# ✅ 正确：必须传完整选项列表（旧+新）
PATCH /v1/data_sources/{id}
{
  "properties": {
    "状态": {
      "select": {
        "options": [
          {"name": "📝 未定稿", "color": "yellow"},   # 新
          {"name": "✅ 已完成", "color": "green"},     # 旧(保持原色)
          {"name": "🔄 进行中", "color": "blue"},      # 旧(保持原色)
          {"name": "⏳ 待跟进", "color": "yellow"}     # 旧(保持原色)
        ]
      }
    }
  }
}
```

### 颜色不能修改
如果传了旧选项但颜色与原始值不同 → **400 error**: `Cannot update color of select with name: xxx.`

**结论：** 添加新选项时必须携带所有旧选项并保持原色。

---

## 3. 属性删除

```bash
# 将属性设为 null 即可删除
PATCH /v1/data_sources/{id}
{
  "properties": {
    "耗时(h)": null    ← 删除此属性
  }
}
```

注意：删除操作不可逆，已有页面中该属性的值会丢失。

---

## 4. Title 属性限制

- 每个数据库只能有**一个** title 属性
- 默认自动创建 `Name` 作为 title
- 不能创建第二个 title 属性 → 400 error: `Cannot create new title property.`
- 不能删除或重命名现有的 title 属性

**实践：** 用默认的 `Name` 当主标题字段，不要试图创建自定义 title。

---

## 5. 创建页面（/v1/pages）

```bash
# ❌ 错误：不能传 is_inline 和顶层 title
POST /v1/pages
{
  "parent": {"page_id": "xxx"},
  "is_inline": false,
  "title": [{"text": {"content": "标题"}}]   ← 报错
}

# ✅ 正确：title 必须嵌套在 properties 里
POST /v1/pages
{
  "parent": {"page_id": "xxx"},
  "properties": {
    "title": {"title": [{"text": {"content": "标题"}}]}
  }
}
```

---

## 6. Database vs Data Source

| 端点 | 用途 | 返回 properties? |
|------|------|:---:|
| `GET /v1/databases/{id}` | 查看数据库信息 | ❌ null |
| `GET /v1/data_sources/{id}` | 查看完整属性定义 | ✅ |
| `POST /v1/data_sources/{id}/query` | 查询数据库条目 | ✅ 条目级别的 properties |
| `PATCH /v1/data_sources/{id}` | 修改属性定义 | N/A |

**规则：** 读/改属性 → 走 data_source；创建页面 → 走 database_id。

---

## 7. Markdown 端点输出大小

`GET /v1/pages/{id}/markdown` 返回的 JSON 可能超过 20000 字符（白皮书类文档可达 80K+）。

**策略：**
- 用 `curl -o` 保存到文件再解析
- 或用 `json_parse()` 处理控制字符
- 不要直接用 `json.loads()` 解析超长响应（会触发 `Invalid control character` 错误）

---

## 8. 有效颜色值列表

```
default, gray, brown, orange, yellow, green, blue, purple, pink, red
```

**无效值：** `teal`, `cyan`, `magenta`, 任何非列表内的颜色名。

---

## 9. 分批写入大数据的实战模式

当治理数据库需要写入 1000+ 条问题时：

1. 使用 `--offset` + `--limit` 实现滑动窗口分批
2. 每批 50-100 条，API 限速约为 0.7-1.5 条/秒
3. 去重指纹为 `{问题类型}:{关联页面ID}`，确保幂等
- 大文件 JSON 解析使用 `json_parse()` 或保存到文件后读取
- 背景终端 + `notify_on_complete=true` 适合长时间写入

---

## 10. 子页面 blocks 中的页面 ID 获取

通过 `GET /v1/blocks/{page_id}/children` 获取子页面列表时，当 block 类型为 `child_page`，页面 ID 就是 **block 本身的 `id`** 字段。不需要再从 `child_page` 对象里取。

```python
for block in children["results"]:
    if block["type"] == "child_page":
        page_id = block["id"]  # ← 直接取 block.id
        title = block["child_page"]["title"]
```

**注意：** blocks 返回的 JSON 可能很大（50-100 个子块时可达 200K+），始终用 `curl -o` 保存到文件再解析。
