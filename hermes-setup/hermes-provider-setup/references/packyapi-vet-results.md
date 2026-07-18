# PackyAPI — full vet results (2026-07-15)

**URL**: https://www.packyapi.com
**Base for API**: `https://www.packyapi.com/v1`
**Site description**: Chinese AI API aggregation platform — "全球领先的 AI API 聚合平台，一站式接入 Claude、Claude Code、GPT、Codex、Gemini、Azure OpenAI"

## Model list

| Model | supported_endpoint_types | Chat Completions | Responses API | Verdict |
|-------|--------------------------|:---:|:---:|---|
| `gpt-5.4` | openai-response, openai | ✅ works | — | Only usable model |
| `gpt-5.4-mini` | openai-response, openai | ❌ protocol_not_supported | — | Broken |
| `gpt-5.5` | openai-response, openai | ❌ protocol_not_supported | — | Broken |
| `gpt-5.6-luna` | openai-response | ❌ | ✅ but output=[] | Responses API empty output |
| `gpt-5.6-sol` | openai-response | ❌ | not tested (same likely) | Responses API |
| `gpt-5.6-terra` | openai-response | ❌ | not tested (same likely) | Responses API |
| `codex-auto-review` | openai-response, openai | ❌ protocol_not_supported | — | Codex-only |

## Billing response

```json
{
  "object": "billing_subscription",
  "has_payment_method": true,
  "soft_limit_usd": 100000000,
  "hard_limit_usd": 100000000,
  "system_hard_limit_usd": 100000000,
  "access_until": 0
}
```

$100M limits = essentially unlimited. Likely a free shared proxy with no real quota enforcement.

## Key quirks

1. **Responses API returns empty output**: gpt-5.6-luna returns `status: completed`, `output: []`, but `output_tokens` shows tokens consumed (5-42). Output is being stripped — the model is designed for Codex CLI agent workflows and auto-injects a massive Codex CLI system prompt (~4000 tokens) into every request.

2. **`instructions` override**: Any `instructions` passed in the request body are ignored and replaced with a hardcoded Codex CLI agent system prompt.

3. **gpt-5.4 is the exception**: The only model that works with standard `/v1/chat/completions`. Response format is standard OpenAI:
   ```json
   {"choices":[{"finish_reason":"stop","index":0,"message":{"content":"1+1等于2。","role":"assistant"}}],...}
   ```

## Hermes config (if you insist)

```yaml
custom_providers:
  - name: packyapi
    base_url: https://www.packyapi.com/v1
    api_key_env: PACKYAPI_API_KEY
    api_mode: chat_completions
    models:
      gpt-5.4: {name: GPT 5.4}
    model: gpt-5.4
```

## Verdict: skip

7 models, only 1 works. The working model (gpt-5.4) is already covered by other providers. The 5.6 series is a tease — Responses API with stripped output.
