# Fallback Curl Research — When web_search/web_extract Fail

> Triggered when Nous Portal credits are exhausted or Firecrawl is unconfigured.
> This file documents the terminal + curl + SOCKS proxy workflow that actually
> works on this machine (Windows 10, Git Bash, 快柠檬 VPN).

---

## The Problem

```
web_search: "Web tools are not configured. Set FIRECRAWL_API_KEY..."
web_extract: "Your Nous Portal account has no usable paid credits..."
```

Both fail simultaneously when:
- Nous Portal credits = 0
- No FIRECRAWL_API_KEY configured
- No self-hosted Firecrawl instance

---

## The Solution: Terminal + curl via SOCKS Proxy

### Proxy Setup

快柠檬 VPN listens on `127.0.0.1:10793` (SOCKS5).

```bash
# Basic pattern
curl -sL --noproxy '*' --max-time 30 -x socks5h://127.0.0.1:10793 'https://example.com/api/endpoint'
```

**Critical flags:**
- `--noproxy '*'` — bypasses the no_proxy env var which includes `127.0.0.1` and would otherwise skip the proxy for localhost
- `-x socks5h://` — SOCKS5 with hostname resolution through proxy (not `socks5://` which resolves locally)
- `-sL` — silent + follow redirects
- `--max-time 30` — timeout

### JSON API Parsing Pattern

```bash
curl -sL --noproxy '*' --max-time 30 -x socks5h://127.0.0.1:10793 'https://api.example.com/v1/models' | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for m in data.get('data', []):
    name = m.get('name', '').lower()
    if 'kimi' in name:
        print(json.dumps(m, indent=2, ensure_ascii=False))
"
```

### HTML Page Text Extraction

```bash
curl -sL --noproxy '*' --max-time 30 -x socks5h://127.0.0.1:10793 'https://example.com/docs' | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:10000])
"
```

### Save to File for Large Responses

```bash
mkdir -p 'C:/Users/win10/AppData/Local/Temp/kimi-research'
curl -sL --noproxy '*' --max-time 30 -x socks5h://127.0.0.1:10793 'https://api.example.com/v1/models' > 'C:/Users/win10/AppData/Local/Temp/kimi-research/response.json'
```

Then read with Python:
```bash
python3 -c "import json; data=json.load(open('C:/Users/win10/AppData/Local/Temp/kimi-research/response.json')); print(len(data.get('data',[])))"
```

**Note:** `/tmp/` maps to Git Bash temp which Python (Windows native) can't access. Use `C:/Users/win10/AppData/Local/Temp/` instead.

---

## Key API Endpoints Verified (2026-07-17)

| Platform | Endpoint | Auth | Notes |
|----------|----------|------|-------|
| **OpenRouter** | `https://openrouter.ai/api/v1/models` | None for listing | Returns 344+ models, searchable |
| **OpenRouter** | `https://openrouter.ai/api/v1/models/{id}/endpoints` | None | Per-model pricing/endpoints |
| **DeepInfra** | `https://api.deepinfra.com/v1/models` | None for listing | 168 models, has K2.5/K2.6/K2.7-Code |
| **Moonshot** | `https://api.moonshot.cn/v1/models` | Bearer <REDACTED> required | Returns 401 without key |
| **Moonshot** | `https://platform.moonshot.cn/docs/pricing` | None | HTML page, extract text |
| **Moonshot** | `https://kimi.moonshot.cn/` | None | Web chat, K3 confirmed available |
| **Ollama** | `https://ollama.com/api/tags?name=moonshot` | None | Public model library |
| **Together** | `https://api.together.xyz/v1/models` | Returns "Missing API key" | No public listing |
| **SambaNova** | `https://api.sambanova.ai/v1/models` | None | 6 models, no KIMI |
| **GitHub Models** | `https://api.github.com/repos/github/models/contents/models` | None | Returns 404 (not a real API) |

---

## KIMI K3 Specific Research Results (2026-07-17)

### Verdict: No Free API Exists

| Channel | K3 Available | Cost |
|---------|-------------|------|
| Moonshot Official API | ✅ | ❌ Pay-per-token, no free tier |
| Kimi Web Chat | ✅ | ✅ Free (web UI only) |
| OpenRouter | ✅ | ❌ $0.000003/token input, $0.000015/token output |
| DeepInfra | ❌ | — |
| NVIDIA NIM | ❌ | — |
| HuggingFace | ❌ | — |
| All Chinese clouds | ❌ | — |

### OpenRouter K3 Details
- **Model ID**: `moonshotai/kimi-k3`
- **Canonical slug**: `moonshotai/kimi-k3-20260715`
- **Context**: 1,048,576 tokens
- **Pricing**: prompt $0.000003, completion $0.000015, input_cache_read $0.0000003
- **Architecture**: text+image→text (multimodal)
- **Provider**: Moonshot AI (int4 quantization)
- **Uptime**: 99.99%
- **Reasoning**: mandatory, effort=max only

### OpenRouter "Free Variant" Note
OpenRouter has a `:free` suffix for some models (e.g., `meta-llama/llama-3.2-3b-instruct:free`), but **KIMI K3 does NOT have a free variant**. The `?filter=free` parameter in the API returns all models (it's not a real filter), and K3 pricing shows non-zero values.

### Open Weights = Future Local Deployment
OpenRouter lists K3 as "open-weight" — model weights are publicly available. Once GGUF quantization is released, local deployment via Ollama/llama.cpp becomes possible.

### Platform Onboarding Timeline (K3 Case Study)
| Platform | Days After Release | Status |
|----------|-------------------|--------|
| Moonshot Official API | Day 0 | ✅ Available |
| Kimi Web Chat | Day 0 | ✅ Available (free UI) |
| OpenRouter | Day 2 | ✅ Available (paid) |
| DeepInfra | — | ❌ Not yet (only K2.x) |
| NVIDIA NIM | — | ❌ Not yet (only K2.6) |
| HuggingFace | — | ❌ Waiting for weights |
| Chinese clouds | — | ❌ Unlikely in near term |

---

## Common Pitfalls

1. **Forgetting `--noproxy '*'`** — without it, curl skips the proxy for 127.0.0.1 because the env var `no_proxy` includes it
2. **Using `socks5://` instead of `socks5h://`** — `socks5` resolves hostnames locally (fails through proxy), `socks5h` resolves through proxy
3. **Writing to `/tmp/` then reading with Windows Python** — Git Bash `/tmp` maps to a Windows temp path that native Python can't open; use `C:/Users/win10/AppData/Local/Temp/`
4. **Assuming `python3` works** — on this machine, `python3` maps to Windows Store stub; use `python` (Python 3.11.15) or `"C:/Python314/python.exe"`
5. **OpenRouter `?filter=free`** — this query parameter doesn't actually filter; it returns all models regardless

---

## Chinese Cloud Platform Scanning Results (2026-07-17)

### KIMI K3 Availability — All Negative

Scanned 10 domestic cloud platforms for KIMI K3 / Moonshot API integration.
**Result: None carry KIMI K3.**

| Platform | URL | K3 Available | Notes |
|----------|-----|-------------|-------|
| 华为云 ModelArts | huaweicloud.com/product/modelarts.html | ❌ | Returns JS anti-bot obfuscation; models inaccessible via curl |
| 京东云 AI | jdcloud.com/cn/products/jdaip | ❌ | Self-built JoyAI-LLM Flash (MoE); 灵境 AIGC platform aggregates Keling/Vidu/PixVerse/Seedream — no K3 |
| 360 AI | ai.360.cn | ❌ | Full self-built matrix: 360gpt2-pro/turbo/pro-trans/turbo-32k-agent/Zhinao-7B/multimodal/CV/security |
| 网易智企 | netease.im | ❌ | IM/PaaS platform, not LLM API provider; /product/ai returns 404 |
| 浪潮源宇 | inspur.com | ❌ | Returns 404; infrastructure-only (servers/storage/cloud) |
| 中科曙光 | sugon.com | ❌ | Page loads but empty content; HPC infrastructure, no model API |
| 商汤科技 | sensecore.cn | ❌ | Self-built SenseNova (日日新); has free AI Studio trial but no K3 |
| 昆仑万维 | kunlun.com | ❌ | Internet platform (Opera/Star Group/Ark Games), not AI cloud |
| 沐曦集成电路 | metax-tech.com | ❌ | GPU chip designer (MXN/MXC/MXG), no model API |
| 燧原科技 | enflame-tech.com | ❌ | WAF blocks all requests (403); AI accelerator hardware |

### Key Takeaways
- Chinese cloud platforms with model marketplaces (Huawei, JDCloud, 360, SenseTime) push **self-built models** and do not aggregate KIMI K3
- GPU/accelerator companies (Metax, Enflame) are hardware-only, not API platforms
- Infrastructure companies (Inspur, Sugon) don't offer LLM APIs
- For KIMI K3 access: official Moonshot API (paid), Kimi Web Chat (free UI), OpenRouter (paid)

---

## When Curl Also Fails — JS-Heavy SPAs

Many Chinese cloud platforms are JavaScript SPAs where `curl` returns:
- **Empty content** (Huawei anti-bot JS, Sugon)
- **SPA shell HTML** with no model data (JDCloud, SenseTime)
- **403 WAF blocks** (Enflame)
- **404 errors** (Inspur, Netease AI page)

**Pattern:** If `curl | grep -i 'kimi\|moonshot\|k3\|模型'` returns nothing, the page is likely a JS SPA and curl cannot extract the model list. Options:
1. Use `browser_navigate` + `browser_vision` (when browser tools available)
2. Search for a JSON API endpoint (e.g., `/api/models`, `/v1/models`) — some SPAs expose these
3. Check official documentation/API reference pages (often static HTML)
4. Accept that the platform cannot be scraped and report "inaccessible via curl"

### Curl Flag Notes
- `--proxy socks5h://...` and `-x socks5h://...` are equivalent (both work)
- `--noproxy '*'` may not always be needed — test without first; add only if curl skips proxy for localhost
- Some sites block non-browser User-Agent; add `-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"` if needed

---

## Workflow Summary

When web_search/web_extract fail:

1. Identify the API endpoint or page URL you need
2. Use `curl -sL --max-time 30 -x socks5h://127.0.0.1:10793 '<URL>'`
3. Pipe to Python for JSON parsing or HTML text extraction
4. Save large responses to `C:/Users/win10/AppData/Local/Temp/` for later analysis
5. **If curl returns empty/SPA shell/403:** page is JS-rendered; try browser tools or JSON API endpoints
6. Compile findings into structured report

---

*Verified: 2026-07-17 on Windows 10, Git Bash, 快柠檬 VPN (127.0.0.1:10793)*
