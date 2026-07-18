#!/bin/bash
# Working template for multi-model parallel API calls
# Source this file and customize for your debate topic
# Usage: bash C:/Users/win10/AppData/Local/hermes/skills/productivity/multi-model-runtime/references/working-template.sh "你的问题"

source C:/Users/win10/AppData/Local/hermes/.env

TOPIC="${1:-你的问题在这里}"

echo "🎭 多模型辩论开始"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 议题: $TOPIC"
echo ""

# Round 1: Parallel calls
curl -s -X POST "https://jbbtoken.cn/v1/chat/completions" \
  -H "Authorization: Bearer $JBBTOKEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"claude-opus-4-8\",\"messages\":[{\"role\":\"system\",\"content\":\"你是设计总监，10年经验。\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/mm_claude.json &

curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"deepseek-chat\",\"messages\":[{\"role\":\"system\",\"content\":\"你是数据分析师。\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/mm_deepseek.json &

curl -s -X POST "https://api.chatanywhere.tech/v1/chat/completions" \
  -H "Authorization: Bearer $CHATANYWHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-5.6-luna-ca\",\"messages\":[{\"role\":\"system\",\"content\":\"你是营销专家。\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/mm_gpt.json &

curl -s -X POST "https://api.mistral.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"mistral-small-latest\",\"messages\":[{\"role\":\"system\",\"content\":\"你是风控官。\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/mm_mistral.json &

wait

echo "🎨 设计总监 [Claude]:"
python3 -c "import json;d=json.load(open('C:/Users/win10/mm_claude.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo ""
echo "📊 数据分析师 [DeepSeek]:"
python3 -c "import json;d=json.load(open('C:/Users/win10/mm_deepseek.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo ""
echo "📣 营销专家 [GPT]:"
python3 -c "import json;d=json.load(open('C:/Users/win10/mm_gpt.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo ""
echo "🛡️ 风控官 [Mistral]:"
python3 -c "import json;d=json.load(open('C:/Users/win10/mm_mistral.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "辩论结束"
