#!/bin/bash
# find_duplicate_databases.sh — Detect duplicate Notion databases by name
# Usage: source ~/.hermes/.env && bash find_duplicate_databases.sh
# 
# This script lists all databases under the Hermes 数据中心 page
# and warns if multiple databases share the same name (a common source
# of 404 errors when duplicate "兄弟消息板" databases exist).

set -e

PARENT_PAGE_ID="39b86cdd-9a32-81bd-a252-c45cf86c4924"

echo "🔍 扫描 Hermes 数据中心 (页面 $PARENT_PAGE_ID) 下的所有数据库..."
echo ""

children=$(curl -s "https://api.notion.com/v1/blocks/${PARENT_PAGE_ID}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03")

# Extract database titles and IDs
echo "$children" | python3 -c "
import sys, json
data = json.load(sys.stdin)
dbs = []
for block in data.get('results', []):
    if block.get('type') == 'child_database':
        title_obj = block.get('child_database', {}).get('title', [])
        title = ''.join(t.get('plain_text', '') for t in title_obj) if title_obj else '(无标题)'
        dbs.append((title, block['id']))

if not dbs:
    print('✅ 没有找到任何数据库')
    sys.exit(0)

print(f'📊 找到 {len(dbs)} 个数据库:\n')

# Group by name
from collections import Counter
names = [d[0] for d in dbs]
duplicates = {name: count for name, count in Counter(names).items() if count > 1}

for title, bid in dbs:
    dup_flag = ' ← ⚠️ 重复!' if title in duplicates else ''
    print(f'  • {title}  ({bid}){dup_flag}')

if duplicates:
    print(f'\n⚠️  发现 {len(duplicates)} 个重复名称:')
    for name, count in duplicates.items():
        print(f'    {name} — {count} 个副本')
    print('\n💡 修复: 保留属性最全的一个(8个属性)，归档其余副本')
    print('   归档方式: PATCH {\"archived\": true}')
else:
    print('\n✅ 没有重复的数据库名称')
"
