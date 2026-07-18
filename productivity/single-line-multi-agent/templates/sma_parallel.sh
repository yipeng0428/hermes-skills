#!/bin/bash
# SMA Parallel Fusion — 并行融合脚本模板
# 用法: bash sma_parallel.sh "你的问题或任务描述" [output_dir]
# 多个模型并行处理同一问题的不同维度，输出各维度结果
# 前置条件: ~/.hermes/.env 里有对应的 API Key

set -euo pipefail
source "${HOME}/.hermes/.env"

TOPIC="${1:?用法: bash sma_parallel.sh '你的任务'}"
OUTPUT_DIR="${2:-/c/Users/win10}"

echo "=== SMA Parallel: $TOPIC ==="

# ═══════════════════════════════════════════
# 并行发射4路
# ═══════════════════════════════════════════
echo "[1/4] Visual/Design dimension — Claude Sonnet..."
curl -s -X POST "https://jbbtoken.cn/v1/chat/completions" \
  -H "Authorization: Bearer ${JBBTOKEN_API_KEY:?未设置}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {"role": "system", "content": "你是视觉设计分析专家。只从视觉设计维度（配色、排版、构图、视觉层次、差异化、信息密度）分析以下问题，给出有深度、具体的分析。其他维度不要去说。直接输出分析内容，不要元评论。"},
    {"role": "user", "content": "$TOPIC"}
  ],
  "temperature": 0.7,
  "max_tokens": 800
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_par_vis.json" &

echo "[2/4] Business/Strategy dimension — DeepSeek..."
curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY:?未设置}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "你是商业策略分析专家。只从商业角度（定价策略、定位、目标用户、渠道适配、竞争格局、ROI）分析以下问题。给出数据驱动的分析。其他维度不要去说。直接输出分析内容。"},
    {"role": "user", "content": "$TOPIC"}
  ],
  "temperature": 0.7,
  "max_tokens": 800
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_par_biz.json" &

echo "[3/4] Cultural/Insight dimension — GPT-4o..."
curl -s -X POST "https://api.chatanywhere.tech/v1/chat/completions" \
  -H "Authorization: Bearer ${CHATANYWHERE_API_KEY:?未设置}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是文化趋势与用户洞察专家。只从趋势文化与受众洞察（消费趋势、生活方式、地域文化、心理需求、代际差异）角度分析以下问题。给出有洞察力的分析。其他维度不要去说。直接输出内容。"},
    {"role": "user", "content": "$TOPIC"}
  ],
  "temperature": 0.7,
  "max_tokens": 800
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_par_cult.json" &

echo "[4/4] Technical/Execution dimension — DeepSeek..."
curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY:?未设置}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "你是技术落地与执行可行性专家。只从技术实现角度（生产工艺、材质、成本、供应链、落地难度、时间、风险）分析以下问题。其他维度不要去说。直接输出分析内容。"},
    {"role": "user", "content": "$TOPIC"}
  ],
  "temperature": 0.7,
  "max_tokens": 800
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_par_tech.json" &

# 等待全部完成
wait
echo ""
echo "═══ ALL 4 DIMENSIONS COMPLETE ═══"
echo ""

# 输出各维度结果
for DIM in vis biz cult tech; do
  FILE="$OUTPUT_DIR/sma_par_${DIM}.json"
  LABEL=$(case $DIM in
    vis) echo "🎨 视觉设计" ;;
    biz) echo "📊 商业策略" ;;
    cult) echo "🌍 文化洞察" ;;
    tech) echo "⚙️ 技术落地" ;;
  esac)
  echo "━━━ $LABEL ━━━"
  python3 -c "
import json
try:
    d=json.load(open('$FILE'))
    print(d['choices'][0]['message']['content'])
except:
    print('ERROR: ' + json.dumps(d,ensure_ascii=False))
"
  echo ""
done

echo "═══ DONE ═══"
echo "Raw outputs: $OUTPUT_DIR/sma_par_*.json"
echo ""
echo "提示: 将这4个维度的内容粘贴到对话中，让门面AI融合为统一成品。"
