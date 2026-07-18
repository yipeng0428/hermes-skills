# Novita / ARCEE / GMICLOUD API Key Testing Report (2026-07-14)

## Testing Workflow (3-Step Validation)

For any new aggregator-style API provider, use this sequence:

### Step 1 — Authentication Test (OPTIONS/HEAD to /v1/models)

```bash
curl -X GET "<base_url>/models" \
  -H "Authorization: Bearer YOUR_KEY" \
  --max-time 15
```
- `HTTP 200` + model list → Key valid, proceed to Step 2
- `HTTP 401 / 403` → Key invalid/revoked
- `SSL / conn refused` → Network/path issue (see GMICLOUD below)
- Empty response → Wrong base URL

### Step 2 — Model List Extraction (Pick a real model)

Once authenticated, extract a real `model.id` from the list response. Don't
guess model names — use what the API reports.

### Step 3 — Live Invocation (Credit/Balance check)

```bash
curl -X POST "<base_url>/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"model": "<id_from_step2>", "messages": [{"role": "user", "content": "你好"}], "max_tokens": 10}'
```
| Response | Meaning |
|---|---|
| `200` + response body | ✅ Fully working |
| `403 NOT_ENOUGH_BALANCE` | Key valid, needs top-up |
| `403 billing.insufficient_credits` | Key valid, needs credits |
| HTTP timeout / SSL fail | Network-level block |

---

## Provider-Specific Findings

### Novita.AI (`https://api.novita.ai/v3/openai/`)

**Base URL**: `https://api.novita.ai/v3/openai/`
**Auth**: `Bearer sk-...` prefix
**Endpoint shape**: `/chat/completions`, `/models`

| Finding | Detail |
|---|---|
| Model list returns 100+ models | DeepSeek V4 Pro / Flash, Qwen3.7-Max, GLM-5.2, Kimi K2.7 Code, Step-3.7-Flash, MiMo-V2.5, Nemotron-3-Nano, CoBuddy, ERNIE-4.5, etc. |
| Free tier model available | `tencent/hy3` (input: 0 $, output: 0 $) |
| Common key error | `NOT_ENOUGH_BALANCE` (code 403) — key is valid but account has no credits |

**Status**: ✅ Key valid — user needs to top up account to use.

### ARCEE (`https://api.arcee.ai/v1/`)

**Base URL**: `https://api.arcee.ai/v1/`
**Auth**: `Bearer rcai-...` prefix
**Endpoint shape**: `/chat/completions`, `/models`

| Finding | Detail |
|---|---|
| Model list returns 1 model | `trinity-large-thinking` (131K context, supports tools + reasoning) |
| Using `auto` as model name | Returns `model.not_accessible` error — must use exact model ID |
| Common key error | `billing.insufficient_credits` — key is valid but no credits |

**Status**: ✅ Key valid — user needs to add credits to use.

### GMICLOUD (`https://api.gmicloud.ai/v1/`)

**Base URL**: `https://api.gmicloud.ai/v1/`
**Auth**: JWT Bearer token (long `eyJ...` string)

| Finding | Detail |
|---|---|
| SSL handshake failure on Windows | `curl: (35) schannel: failed to receive handshake` on bash/MSYS curl (Windows) |
| HTTP (no SSL) returns empty body | Server likely redirects to HTTPS |
| Probable root cause | Server-side SSL/TLS misconfiguration or region-restricted access |
| Recommendation | Test from a non-Windows machine or via `execute_code` + Python's `urllib` with custom SSL context |

**Status**: ⚠️ Cannot validate — SSL issue blocks connection entirely.

---

## Known LLM API Providers Master List (2026)

### Tier 1 — Major / Stable
| Provider | Base URL Shape | Auth Prefix | Notes |
|---|---|---|---|
| Nous Portal | Internal OAuth | — | 300+ models, bundled |
| OpenRouter | `openrouter.ai/api/v1` | `sk-or-...` | 300+ models aggregator |
| novita.ai | `novita.ai/v3/openai/` | `sk-...` | 100+ models, low cost |
| DeepSeek | `platform.deepseek.com` | `sk-...` | V3, R1, Coder |
| Anthropic | `api.anthropic.com` | `sk-ant-...` | Claude 4.x series |
| OpenAI / Codex | `api.openai.com` | `sk-...` | GPT-4o / GPT-5 |
| xAI Grok | `api.x.ai` | `sk-...` or OAuth | Grok-2 / Grok-3 |
| Google AI Studio | `generativelanguage.googleapis.com` | API key | Gemini 2.x |
| GoogleVertex | `us-central1-aiplatform.googleapis.com` | OAuth/ADC | Gemini via GCP |
| Mistral | `api.mistral.ai` | API key | Mistral Large / Small |
| HuggingFace | `api-inference.huggingface.co` | `hf_...` | 400K+ open models |

### Tier 2 — Regional / China
| Provider | Base URL Shape | Auth Prefix | Notes |
|---|---|---|---|
| 智谱 GLM (Z.AI) | `open.bigmodel.cn/api/paas/v4` | `xxxx.yyyy` | glm-4-flash, glm-4 |
| 阿里 DashScope | `dashscope.aliyun.com` | `sk-...` | Qwen3 / Qwen2.5 |
| 字节 火山引擎 | `open.volcengineapi.com` | `...` | Doubao / Seed |
| 月之暗面 Kimi | `api.moonshot.cn` | `sk-...` | Kimi K2.x |
| 腾讯 混元 | `hunyuan.tencentcloudapi.com` | SecretId/Key | HY3 / 混元 |
| 百度 文心 | `aip.baidubce.com` | `...` | ERNIE 4.5 |
| 阶跃星辰 StepFun | `api.stepfun.com` | API key | Step-1 / Step-2 |
| MiniMax | `api.minimaxi.chat` | API key | M3 / ABAB |
| Sense Nova | `token.sensenova.cn/v1` | `...` | Various (Chinese SenseTime) |

### Tier 3 — Aggregators / Relays
| Provider | Base URL Shape | Auth Prefix | Notes |
|---|---|---|---|
| jbbtoken | `jbbtoken.cn` | `sk-...` | Claude series relay |
| ChatAnywhere | `chatanywhere.tech` | `sk-...` | GPT series relay |
| ARCEE | `api.arcee.ai/v1` | `rcai-...` | Trinity series |
| Kilo Code | `kilocode.ai` | API key | Coding models |
| Electron | `api.eleuther.ai` | API key | Open-source |

---

## Pitfalls When Adding a New Provider

1. **Verify before committing** — Test auth → model list → live call before adding to config
2. **Check balance after verify** — Many keys "work" but have zero quota; test the actual invocation
3. **Use exact model IDs from /models** — Never guess; names like `qwen3-8b` or `auto` often fail
4. **Watch for SSL quirks** — Windows curl (schannel) may reject valid certs that Linux/Python accept
5. **Never inline keys in config.yaml** — Always use `api_key_env: VAR_NAME` → `.env` pattern
6. **Duplicate base URLs** — Some relays share the same endpoint shape but different prefix/auth; confirm with real list call before assuming

