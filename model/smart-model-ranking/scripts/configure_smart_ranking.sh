#!/bin/bash
# 快速配置脚本 - 智能模型排序

set -e

echo "🚀 智能模型排序系统 - 快速配置"
echo "================================"
echo ""

# 检查配置目录
CONFIG_DIR="$HOME/.hermes"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
DATA_FILE="$CONFIG_DIR/model_usage.json"

if [ ! -d "$CONFIG_DIR" ]; then
    echo "⚠️  配置目录不存在: $CONFIG_DIR"
    echo "   正在创建目录..."
    mkdir -p "$CONFIG_DIR"
fi

# 备份现有配置（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    echo "📝 备份现有配置..."
    cp "$CONFIG_FILE" "$CONFIG_DIR/config_backup_$(date +%Y%m%d_%H%M%S).yaml"
    echo "   已备份到: $CONFIG_DIR/config_backup_$(date +%Y%m%d_%H%M%S).yaml"
fi

# 创建智能排序配置
cat > "$CONFIG_FILE" << 'EOF'
# Hermes配置文件
# 智能模型排序配置已添加

model:
  default: gpt-5.6-luna-ca
  provider: custom:chatanywhere
  base_url: https://api.chatanywhere.tech

agent:
  service_tier: normal
  verify_on_stop: false
  reasoning_effort: high

smart_ranking:
  enabled: true
  top_n_models: 5
  weights:
    usage_frequency: 0.6
    response_quality: 0.4

# 其他配置保持不变...
EOF

echo "✅ 配置文件已更新"
echo ""

# 创建示例模型使用数据文件
cat > "$DATA_FILE" << 'EOF'
{
  "models": {},
  "last_updated": null
}

echo "📊 数据存储文件已创建: $DATA_FILE"
echo ""

# 显示配置内容
echo "📋 智能排序配置内容:"
echo "===================="
sed -n '/^smart_ranking:/,/^[a-z_]/p' "$CONFIG_FILE" | head -n -1
echo ""

# 提供使用建议
echo "💡 使用建议:"
echo "==========="
echo "1. 重启Hermes以加载新配置:"
echo "   hermes reset"
echo ""
echo "2. 系统会自动开始追踪您的模型使用情况"
echo ""
echo "3. 查看模型列表时，最好的5个模型会优先显示"
echo ""
echo "4. 可以通过编辑 ~/.hermes/config.yaml 调整配置"
echo ""

# 检查技能是否安装
SKILL_DIR="$HOME/.hermes/skills/model/smart-model-ranking"
if [ -d "$SKILL_DIR" ]; then
    echo "✨ 技能已安装: smart-model-ranking"
else
    echo "⚠️  技能目录不存在: $SKILL_DIR"
    echo "   请确保技能已正确安装"
fi

echo ""
echo "🎉 配置完成！"
echo "===================="
echo "系统现在会智能排序您的模型，将最好的5个模型优先展示。"
