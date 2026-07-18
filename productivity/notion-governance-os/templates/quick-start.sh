#!/bin/bash
# Notion 治理系统 - 快速启动脚本
# 使用前请确保已配置 NOTION_API_KEY 到 ~/.hermes/.env

set -e

echo "🚀 Notion 治理系统 - 快速启动"
echo "================================"
echo ""

# 检查环境
if [ ! -f "$HOME/.hermes/.env" ]; then
    echo "❌ 未找到 ~/.hermes/.env 文件"
    echo "请先配置 Notion API Key"
    exit 1
fi

if ! grep -q "NOTION_API_KEY" "$HOME/.hermes/.env"; then
    echo "❌ 未在 .env 文件中找到 NOTION_API_KEY"
    echo "请添加: NOTION_API_KEY=ntn_your_token_here"
    exit 1
fi

# 切换到脚本目录
SCRIPT_DIR="$HOME/.hermes/scripts/notion-governance"
cd "$SCRIPT_DIR" || exit 1

echo "✅ 环境检查通过"
echo ""

# 步骤 1: 运行全量扫描
echo "🔍 步骤 1/4: 运行全量扫描..."
python scanner.py --full --output "$HOME/.hermes/reports/scan_initial.json"
echo "✅ 全量扫描完成"
echo ""

# 步骤 2: 查看扫描摘要
echo "📊 步骤 2/4: 查看扫描摘要..."
echo "问题统计:"
jq '.summary' "$HOME/.hermes/reports/scan_initial.json" 2>/dev/null || cat "$HOME/.hermes/reports/scan_initial.json" | python -m json.tool | grep -A 10 summary
echo ""

# 步骤 3: 写入治理数据库
echo "📋 步骤 3/4: 写入治理数据库..."
python dashboard.py "$HOME/.hermes/reports/scan_initial.json"
echo "✅ 已写入治理数据库"
echo ""

# 步骤 4: 查看治理面板
echo "🛡️ 步骤 4/4: 查看治理面板..."
echo "治理数据库地址: https://app.notion.so/p/02d80532c500486c92e1ec374f51b06c"
echo ""

# 可选步骤 5: 自动修复
echo "⚡ 可选步骤 5/5: 自动修复..."
echo "是否要运行自动修复？ (y/n)"
read -r answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    python fixer.py "$HOME/.hermes/reports/scan_initial.json" --dry-run
    echo "是否确认执行修复？ (y/n)"
    read -r confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        python fixer.py "$HOME/.hermes/reports/scan_initial.json"
        echo "✅ 自动修复完成"
    fi
fi

echo ""
echo "🎉 快速启动完成！"
echo ""
echo "📚 下一步建议:"
echo "  1. 查看治理面板中的问题列表"
echo "  2. 设置定时任务: hermes cronjob create ..."
echo "  3. 定期运行: python scanner.py --incremental"
echo ""

# 显示健康评分
echo "💖 你的 Notion 知识库健康评分:"
python -c "
import json
with open('$HOME/.hermes/reports/scan_initial.json') as f:
    data = json.load(f)
    print(f\"  分数: {data['summary']['health_score']}/100\")
    if data['summary']['health_score'] >= 90:
        print('  🌟 状态: 优秀')
    elif data['summary']['health_score'] >= 70:
        print('  👍 状态: 良好')
    elif data['summary']['health_score'] >= 50:
        print('  🟡 状态: 需要关注')
    else:
        print('  🔴 状态: 需要立即处理')
"

echo ""
echo "🔗 治理系统文档: 加载技能 'notion-governance-os' 查看详细文档"
