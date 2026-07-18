---
name: multi-model-runtime
description: "Battle-tested patterns for calling multiple LLM APIs in parallel from terminal. Source env vars, avoid quote-escape hell, run parallel curl, collect results."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-model, parallel, api, curl, terminal, execution, runtime, 多模型, 并行调用]
    related_skills: [yuanbao, multi-agent-debate, mixture-of-agents]
---

# Multi-Model Runtime Patterns

## What It Is

Battle-tested patterns for calling **multiple LLM APIs in parallel** from Hermes terminal. Covers the gap between "theoretically we can call N models" and "actually getting N responses without quote-escape hell or auth failures."

## When to Use

- Running Yuanbao multi-model debates
- Any task that needs 2+ different LLM perspectives
- Ensemble / committee model voting
- Cross-validation of AI outputs

## The 7 Deadly Sins of Multi-Model Execution

### Sin 1: execute_code is BLOCKED for API calls

```python
# FAILS — security policy blocks raw urllib/subprocess in execute_code
import urllib.request  # ← BLOCKED
```

**Fix**: Use `terminal` with `curl` commands instead.

### Sin 2: Environment variables are NOT exported

```bash
# FAILS — env vars from .env are not in shell scope
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" ...  # ← empty
```

**Fix**: Always source first:
```bash
source C:/Users/win10/AppData/Local/hermes/.env
```

### Sin 3: Inline JSON in bash causes quote-escape hell

```bash
# FAILS — nested quotes break
curl -d '{"model":"claude-opus-4-8","messages":[{"role":"system","content":"..."}]}'
# bash: unexpected EOF while looking for matching `"'
```

**Fix**: Write a `.sh` script file with heredoc:
```bash
cat > C:/Users/win10/yuanbao_run.sh << 'SCRIPT'
#!/bin/bash
source C:/Users/win10/AppData/Local/hermes/.env
curl -s -X POST "https://jbbtoken.cn/v1/chat/completions" \
  -H "Authorization: Bearer $JBBTOKEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-opus-4-8","messages":[...]}' \
  -o C:/Users/win10/yuanbao_claude.json &
wait
SCRIPT

bash C:/Users/win10/yuanbao_run.sh
```

### Sin 4: Foreground mode rejects '&' backgrounding

```bash
# FAILS
curl ... &  # "Foreground command uses '&' backgrounding"
```

**Fix**: Use `terminal(background=true)` + `process(action="wait")`:
```
terminal(background=true, command="bash C:/Users/win10/yuanbao_run.sh", timeout=120)
process(action="wait", session_id="...", timeout=60)
```

### Sin 5: Per-provider API Key pitfalls

| Provider | Env Var | Auth Header | Known Quirks |
|----------|---------|-------------|--------------|
| jbbtoken (Claude) | `JBBTOKEN_API_KEY` | `Bearer $JBBTOKEN_API_KEY` | Do NOT use `DEEPSEEK_API_KEY` |
| deepseek | `DEEPSEEK_API_KEY` | `Bearer sk-...` | Must be `sk-` prefixed |
| chatanywhere (GPT) | `CHATANYWHERE_API_KEY` | `Bearer $CHATANYWHERE_API_KEY` | Working |
| mistral | `MISTRAL_API_KEY` | `Bearer $MISTRAL_API_KEY` | May return Unauthorized |

### Sin 6: Interleaved output from parallel curls

```bash
# BAD — all models write to stdout, interleaved
curl ... & curl ... & curl ... & wait
```

**Fix**: Each model writes to its own file, parse after wait:
```bash
curl ... -o C:/Users/win10/yuanbao_claude.json &
curl ... -o C:/Users/win10/yuanbao_deepseek.json &
curl ... -o C:/Users/win10/yuanbao_gpt.json &
wait

python3 -c "import json;d=json.load(open('C:/Users/win10/yuanbao_claude.json'));print(d['choices'][0]['message']['content'])"
```

### Sin 7: Silently dropping failed models

If a model returns an error (504, auth fail, unauthorized), EXPLICITLY state:
- Which expert role was lost
- What perspective is now missing
- Whether other models partially cover the gap

## Complete Working Template

```bash
#!/bin/bash
source C:/Users/win10/AppData/Local/hermes/.env

# Define the topic/question
TOPIC="你的问题在这里"

# Round 1: Parallel calls to 4 models
curl -s -X POST "https://jbbtoken.cn/v1/chat/completions" \
  -H "Authorization: Bearer $JBBTOKEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"claude-opus-4-8\",\"messages\":[{\"role\":\"system\",\"content\":\"你是设计总监...\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/yuanbao_claude.json &

curl -s -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"deepseek-chat\",\"messages\":[{\"role\":\"system\",\"content\":\"你是数据分析师...\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/yuanbao_deepseek.json &

curl -s -X POST "https://api.chatanywhere.tech/v1/chat/completions" \
  -H "Authorization: Bearer $CHATANYWHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-5.6-luna-ca\",\"messages\":[{\"role\":\"system\",\"content\":\"你是营销专家...\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/yuanbao_gpt.json &

curl -s -X POST "https://api.mistral.ai/v1/chat/completions" \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"mistral-small-latest\",\"messages\":[{\"role\":\"system\",\"content\":\"你是风控官...\"},{\"role\":\"user\",\"content\":\"$TOPIC\"}],\"temperature\":0.7,\"max_tokens\":800}" \
  -o C:/Users/win10/yuanbao_mistral.json &

wait

# Parse results
echo "=== Claude ==="
python3 -c "import json;d=json.load(open('C:/Users/win10/yuanbao_claude.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo "=== DeepSeek ==="
python3 -c "import json;d=json.load(open('C:/Users/win10/yuanbao_deepseek.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo "=== GPT ==="
python3 -c "import json;d=json.load(open('C:/Users/win10/yuanbao_gpt.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"

echo "=== Mistral ==="
python3 -c "import json;d=json.load(open('C:/Users/win10/yuanbao_mistral.json'));print(d['choices'][0]['message']['content'] if 'choices' in d else json.dumps(d,ensure_ascii=False))"
```

## Model Response Styles (for role assignment)

| Model | Style | Best for |
|-------|-------|---------|
| Claude Opus 4.8 | Structured, cautious, precise | Design, compliance, technical accuracy |
| DeepSeek V4 | Data-heavy, conservative, Chinese-market | Financial analysis, ROI, market data |
| GPT-5.6 Luna | Comprehensive, marketing-native | Marketing strategy, consumer insight |
| Mistral Small | Concise, direct, skeptical | Risk identification, devil's advocate |

## Panel Size Guide

| Size | When to use | Trade-off |
|------|-------------|-----------|
| 3 models | Quick decisions, limited budget | Fast, but one failure = 33% loss |
| 4 models | Standard strategic questions | Good redundancy |
| 5 models | High-stakes (>$100k) | Maximum coverage, higher cost |

## Cross-Examination Round (Round 2)

Usually unnecessary. Round 1 from 3-4 different models already provides enough diversity. Skip Round 2 unless:
- Models disagree significantly in Round 1
- Decision is high-stakes
- User explicitly asks for deeper debate

## Reliability Record (2026-07-15)

| Model | Provider | Status | Notes |
|-------|----------|--------|-------|
| Claude Opus 4.8 | jbbtoken | ✅ | Use JBBTOKEN_API_KEY, not DEEPSEEK_API_KEY |
| DeepSeek V4 | deepseek | ✅ | Auth header must be `Bearer sk-...` |
| GPT-5.6 Luna | chatanywhere | ✅ | Worked on first try |
| Mistral Small | mistral | ❌ | `{"detail":"Unauthorized"}` — key needs refresh |
