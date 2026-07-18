#!/bin/bash
# SMA Serial Refinement — 串行精炼脚本模板
# 用法: bash sma_serial.sh "你的问题或任务描述" [output_dir]
# 将 TOPIC 替换为实际内容，修改 model/provider/key 后使用
# 前置条件: ~/.hermes/.env 里有对应的 API Key

set -euo pipefail
source "${HOME}/.hermes/.env"

TOPIC="${1:?用法: bash sma_serial.sh '你的任务'}"
OUTPUT_DIR="${2:-/c/Users/win10}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== SMA Serial: $TOPIC ==="
echo "Output: $OUTPUT_DIR/sma_serial_*.json"

# ═══════════════════════════════════════════
# Round 1: 初稿创建 — 替换为你选择的模型
# ═══════════════════════════════════════════
echo "[1/3] Creating draft with DeepSeek..."
curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY:?未设置 DEEPSEEK_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "你是一个顶级行业分析专家，擅长结构化的、有深度的分析。请完整回答以下问题，直接输出内容，不要加元评论。"},
    {"role": "user", "content": "$TOPIC"}
  ],
  "temperature": 0.7,
  "max_tokens": 1500
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_serial_r1.json"

if [ $? -ne 0 ] || [ ! -s "$OUTPUT_DIR/sma_serial_r1.json" ]; then
  echo "❌ Round 1 FAILED — check network/key"; exit 1
fi

R1_CONTENT=$(python3 -c "
import json
d=json.load(open('$OUTPUT_DIR/sma_serial_r1.json'))
print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))
")

echo "  Draft length: ${#R1_CONTENT} chars"

# ═══════════════════════════════════════════
# Round 2: 质检+补充 — 换不同模型
# ═══════════════════════════════════════════
echo "[2/3] Enhancing with Claude Sonnet..."
ESCAPED_R1=$(printf '%s' "$R1_CONTENT" | python3 -c "import sys,json;print(json.dumps(sys.stdin.read()))")

curl -s -X POST "https://jbbtoken.cn/v1/chat/completions" \
  -H "Authorization: Bearer ${JBBTOKEN_API_KEY:?未设置 JBBTOKEN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {"role": "system", "content": "你是一个挑剔的质检专家+内容增强专家。给定初稿，你必须：1)补充遗漏的重要维度；2)纠正事实错误；3)增加深度和具体案例；4)提升说服力。输出完整的修改版，不只是【改正清单】。"},
    {"role": "user", "content": "以下是初稿，请质检+补充+增强为新版：\n\n${ESCAPED_R1:0:6000}"}
  ],
  "temperature": 0.6,
  "max_tokens": 1500
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_serial_r2.json"

R2_CONTENT=$(python3 -c "
import json
d=json.load(open('$OUTPUT_DIR/sma_serial_r2.json'))
print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))
")

echo "  Enhanced length: ${#R2_CONTENT} chars"

# ═══════════════════════════════════════════
# Round 3: 润色 — 再用不同模型
# ═══════════════════════════════════════════
echo "[3/3] Polishing with GPT-4o..."
ESCAPED_R2=$(printf '%s' "$R2_CONTENT" | python3 -c "import sys,json;print(json.dumps(sys.stdin.read()))")

curl -s -X POST "https://api.chatanywhere.tech/v1/chat/completions" \
  -H "Authorization: Bearer ${CHATANYWHERE_API_KEY:?未设置 CHATANYWHERE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是一个世界级的表达与润色专家。任务：1)统一语调，确保全文读起来像一个自信专家的手笔；2)消除AI腔（不说【值得注意的是】【总而言之】）；3)打磨节奏；4)保持内容完整性。输出最终成品，不解释你改了什么。"},
    {"role": "user", "content": "请将以下内容打磨为最终可交付的精品：\n\n${ESCAPED_R2:0:8000}"}
  ],
  "temperature": 0.5,
  "max_tokens": 2000
}
EOF
)" \
  -o "$OUTPUT_DIR/sma_serial_final.json"

# 输出最终结果
echo ""
echo "═══ FINAL OUTPUT ═══"
python3 -c "
import json
d=json.load(open('$OUTPUT_DIR/sma_serial_final.json'))
print(d['choices'][0]['message']['content'] if 'choices' in d else 'ERROR: ' + json.dumps(d,ensure_ascii=False))
"
echo ""
echo "═══ DONE ═══"
echo "Raw outputs: $OUTPUT_DIR/sma_serial_*.json"
