#!/usr/bin/env python3
"""
收件箱 → 每周事务 一键转入脚本
用法:
  python inbox-to-task.py                    # 转入所有未转入项
  python inbox-to-task.py --dry-run          # 预览将要转入的项
  python inbox-to-task.py --id <page_id>     # 只转入指定项
  python inbox-to-task.py --priority "🔥 现在就做"  # 按优先级筛选
"""

import requests, json, os, sys, argparse
from datetime import date

NOTION_KEY = os.environ.get("NOTION_API_KEY", "")
HEADERS = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

# Database IDs — override via env vars or edit inline
INBOX_DS_ID = os.environ.get("NOTION_INBOX_DS_ID", "58324c59-26fe-4c52-8809-7cfccf707b74")
WEEKLY_DB_ID = os.environ.get("NOTION_WEEKLY_DB_ID", "97eba705-25a9-40d6-98ec-db082d171e26")

# Priority mapping: Inbox → Weekly Tasks
PRIORITY_MAP = {
    "🔥 现在就做": "🔥 P0 紧急",
    "⚡ 本周": "⚡ P1 高",
    "📌 本月": "📌 P2 正常",
    "💤 以后再说": "💤 P3 低",
}

# Type to 任务类别 mapping (best effort)
TYPE_CATEGORY_MAP = {
    "📌 待办": "✅ 其他",
    "💡 想法": "📈 计划总结",
    "🔭 远期目标": "📈 计划总结",
    "📚 想学的": "💻 内部事务",
    "🗑️ 可能放弃": "✅ 其他",
}


def get_inbox_items(priority_filter=None, page_id=None):
    """Query inbox items that haven't been transferred."""
    url = f"https://api.notion.com/v1/data_sources/{INBOX_DS_ID}/query"

    filter_clause = {
        "property": "已转入",
        "checkbox": {"equals": False},
    }

    body = {
        "page_size": 100,
        "filter": filter_clause,
        "sorts": [{"property": "优先级", "direction": "descending"}],
    }

    r = requests.post(url, headers=HEADERS, json=body)
    r.raise_for_status()
    results = r.json().get("results", [])

    items = []
    for page in results:
        props = page["properties"]
        title = "".join(
            t.get("plain_text", "")
            for t in props.get("Name", {}).get("title", [])
        )
        pri = props.get("优先级", {}).get("select", {})
        typ = props.get("类型", {}).get("select", {})
        note = "".join(
            t.get("plain_text", "") for t in props.get("备注", {}).get("rich_text", [])
        )
        source = "".join(
            t.get("plain_text", "") for t in props.get("来源", {}).get("rich_text", [])
        )

        if page_id and page["id"] != page_id:
            continue
        if priority_filter and pri.get("name") != priority_filter:
            continue

        items.append(
            {
                "id": page["id"],
                "title": title,
                "priority": pri.get("name", ""),
                "type": typ.get("name", ""),
                "note": note,
                "source": source,
            }
        )

    return items


def create_weekly_task(item):
    """Create a page in 每周事务 from an inbox item."""
    mapped_priority = PRIORITY_MAP.get(item["priority"], "📌 P2 正常")
    mapped_category = TYPE_CATEGORY_MAP.get(item["type"], "✅ 其他")

    note_parts = ["📥 从收件箱转入"]
    if item.get("note"):
        note_parts.append(f"原备注: {item['note']}")
    if item.get("source"):
        note_parts.append(f"来源: {item['source']}")

    body = {
        "parent": {"database_id": WEEKLY_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": item["title"]}}]},
            "状态": {"select": {"name": "📅 计划"}},
            "优先级": {"select": {"name": mapped_priority}},
            "任务类别": {"select": {"name": mapped_category}},
            "日期": {"date": {"start": date.today().isoformat()}},
            "备注": {"rich_text": [{"text": {"content": " | ".join(note_parts)}}]},
        },
    }

    r = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=body)
    r.raise_for_status()
    new_page = r.json()
    return new_page["id"]


def link_and_mark(inbox_item_id, weekly_page_id):
    """Set relation and mark as transferred."""
    body = {
        "properties": {
            "关联事务": {"relation": [{"id": weekly_page_id}]},
            "已转入": {"checkbox": True},
        }
    }
    r = requests.patch(
        f"https://api.notion.com/v1/pages/{inbox_item_id}", headers=HEADERS, json=body
    )
    r.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="收件箱 → 每周事务 一键转入")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")
    parser.add_argument("--id", help="只转入指定 page_id")
    parser.add_argument("--priority", help="按优先级筛选")
    args = parser.parse_args()

    items = get_inbox_items(priority_filter=args.priority, page_id=args.id)

    if not items:
        print("📭 没有待转入的收件箱项目")
        return

    print(f"📥 找到 {len(items)} 个待转入项目:\n")

    for i, item in enumerate(items, 1):
        prefix = "🔍 [预览]" if args.dry_run else "🔄"
        print(f"  {prefix} [{item['priority']}] {item['title']}")
        print(f"        → 任务类别: {TYPE_CATEGORY_MAP.get(item['type'], '✅ 其他')}")
        print(f"        → 优先级: {PRIORITY_MAP.get(item['priority'], '📌 P2 正常')}")

        if not args.dry_run:
            try:
                weekly_id = create_weekly_task(item)
                link_and_mark(item["id"], weekly_id)
                print(f"        ✅ 已转入 → {weekly_id[:8]}...")
            except Exception as e:
                print(f"        ❌ 失败: {e}")

        print()

    if args.dry_run:
        print("💡 这是预览模式。去掉 --dry-run 执行实际转入。")
    else:
        print(f"✅ 完成！已转入 {len(items)} 个项目到「每周事务」")


if __name__ == "__main__":
    main()
