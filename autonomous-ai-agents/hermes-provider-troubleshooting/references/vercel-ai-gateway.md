# Vercel AI Gateway — Key Requirements & Troubleshooting

## Overview

Vercel AI Gateway provides a unified API endpoint (`gatewayai.vercel.ai`) to access hundreds of AI models. However, **an API Key alone is not sufficient** — the key must be bound to an active Vercel Project/Deployment.

## Key Format

Vercel AI Gateway API keys use the prefix `vck_`:
```
vck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Common Error: DEPLOYMENT_NOT_FOUND

**Symptom:** All API calls return HTTP 404 with:
```json
{
  "error": "The deployment could not be found on Vercel.",
  "code": "DEPLOYMENT_NOT_FOUND"
}
```

**Root Cause:** The API Key is valid but has no associated Vercel Project/Deployment. This happens when:
1. The user generated a key but never created a Vercel Project
2. The Project the key was bound to was deleted
3. The account onboarding is incomplete

**Fix:**
1. Go to https://vercel.com/new and create any project (even a simple HTML page)
2. Deploy the project
3. In the project settings, enable AI Gateway
4. Generate a new API Key bound to that project
5. The new key will work

## Free Tier

Vercel AI Gateway has a free tier with monthly credits. Exceeding credits requires payment method binding. The free tier is sufficient for light usage.

## Endpoint

```
POST https://gatewayai.vercel.ai/v1/chat/completions
Authorization: Bearer vck_...
```

## Model Naming Convention

Models are referenced as `provider/model-id`:
- `openai/gpt-4o-mini`
- `anthropic/claude-3-5-sonnet-20241022`
- `google/gemini-1.5-flash`

## Verification Command

```bash
curl -s -X POST "https://gatewayai.vercel.ai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer vck_..." \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

**Expected success:** HTTP 200 with chat completion response.
**DEPLOYMENT_NOT_FOUND:** Key is valid but no project exists — create one first.
**401/403:** Key is invalid or revoked.
