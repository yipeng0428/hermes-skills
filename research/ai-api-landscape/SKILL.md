---
name: ai-api-landscape
description: "Research and inventory free/paid AI API platforms (LLM, image, voice) across global and Chinese markets. Build structured comparison reports with verified official pricing tiers."
version: 1.0.0
tags: [ai-api, free-tier, llm, speech, image, research, comparison, pricing]
platforms: [linux, macos, windows]
---

# AI API Landscape — Free & Paid Tier Research

## Trigger
When the user asks to find, compare, or inventory AI API platforms — especially
free tiers, trial credits, rate-limited free models, or pricing tiers for LLM /
image generation / speech (STT/TTS) APIs — both international and Chinese domestic.

## Critical Distinction
**FREE API ≠ FREE WEB UI.** Many platforms advertise "free" for their web chat
product (e.g. ChatGPT Free, Kimi Chat Free) but their developer API has no free
tier. Always verify against official **pricing/docs/API reference** pages,
never rely on blog aggregator articles.

## Workflow (for broad, multi-market surveys)

### Phase 1: Parallel Sub-Agent Delegation
For large-scope surveys (30+ platforms across multiple markets), spawn **3 parallel
sub-agents** to avoid context flooding:

1. **China LLM platforms** — Aliyun Bailian/Tongyi, Volcano Ark/Doubao, Baidu Qianfan/ERNIE,
   Tencent Hunyuan, Zhipu BigModel, DeepSeek, SiliconFlow, Moonshot/Kimi, MiniMax,
   Stepfun, iFlytek Spark, SenseTime, OpenXLab, etc.
2. **International LLM/multimodal platforms** — Google AI Studio/Gemini, Groq,
   OpenRouter, HuggingFace Inference, Cloudflare Workers AI, Cerebras, SambaNova,
   GitHub Models, Mistral, Cohere, Together, Fireworks, NVIDIA NIM, Anthropic,
   OpenAI, xAI, Perplexity, AI21, etc.
3. **Image + Speech APIs (global)** — Replicate, fal.ai, Stability AI, HuggingFace,
   Cloudflare, Google/Gemini/Imagen, Together, DeepInfra, Segmind, Leonardo, Clipdrop;
   Groq Whisper, OpenAI audio, ElevenLabs, Deepgram, AssemblyAI, Gladia, Azure Speech,
   Google Cloud Speech/TTS, AWS Polly/Transcribe, Cartesia, PlayHT, Fish Audio;
   and Chinese equivalents (Aliyun Intelligent Speech/Wanxiang, Tencent Cloud Speech,
   Baidu AI Cloud Speech, iFlytek, Volcano Engine Speech/Jimeng, MiniMax Hailuo).

Each sub-agent must return **per-platform structured fields**:
- Platform name, API type, free tier nature (permanent free / monthly free / one-time trial credits / free model rate-limited)
- Coverage models, exact quota / rate limits, expiration, card/identity requirements
- Official doc link, verification date, uncertainties noted

Sub-agents should use web_search + web_extract (prefer official docs URLs).
Context must include: language preference, current date note, and the
"verify against official docs, not aggregators" instruction.

### Phase 2: Direct Browser Verification (critical)
When sub-agents return or web_extract is unavailable, **open pricing/docs pages
directly in browser** and verify key data points:

1. `browser_navigate` → official pricing/rate-limit page
2. `browser_vision` → read exact tables (free tier quotas, RPM/TPM/RPD limits)
3. `browser_console` → `document.querySelectorAll('table')` to extract raw table data
4. Cross-reference search snippets against live page content

### Phase 3: Tier Classification & Deliverable
Classify every platform into one of 4 categories:
- ✅ **Permanent/monthly recurring free** — e.g. Google Gemini free tier, Groq free plan
- 🆓 **Free models, rate-limited only** — e.g. Cerebras all models free, OpenRouter :free
- 🎁 **One-time new-user credits** — e.g. Aliyun Bailian 新人赠送, Tencent Hunyuan 资源包
- ❌ **No free API** — e.g. Together AI ($5 minimum), Replicate (pure pay-as-you-go)

Deliver a structured Markdown file with sections for:
1. International text/multimodal LLM APIs
2. China domestic text/multimodal LLM APIs
3. Voice APIs (STT / TTS) — international + domestic
4. Image/vision APIs
5. Quick selection guide (by scenario: zero-barrier, China-friendly, most generous)

Include verification date, official links for every platform, and a disclaimer
that policies change.

## Pitfalls
- **Chinese cloud platforms are JS SPAs** — Huawei ModelArts, JDCloud, SenseTime, and others return empty content, SPA shell HTML, 403 WAF blocks, or 404 errors when scraped with curl. They are JavaScript Single-Page Applications that require browser rendering. Options: (1) use browser_navigate + browser_vision if available, (2) hunt for JSON API endpoints like `/api/models` or `/v1/models` that some SPAs expose, (3) check official API reference docs (often static HTML), (4) report "inaccessible via curl" rather than retrying blindly.
- **web_extract breaks on Chinese cloud docs** (Aliyun, Tencent Cloud, Volcengine)
  These sites have aggressive anti-scraping; fall back to browser.
- **Cohere docs have cookie consent popups** that block the table. Use
  `browser_console` to `document.querySelectorAll('table')` directly instead.
- **Azure pricing page** is massive with region/currency selectors. For F0 tier
  specifics, prefer web_search with `site:learn.microsoft.com` queries.
- **fal.ai "free credits"** are Sandbox-only, NOT usable through API. Carefully
  distinguish Playground credits from API credits.
- **Zhipu BigModel** has "GLM Coding Plan" subscriptions with per-5-hour limits —
  this is NOT a traditional free API tier; don't misclassify it.
- **web_search / web_extract may fail** if Nous Portal credits are exhausted or
  Firecrawl is unconfigured. When this happens, **fall back to terminal + curl
  via SOCKS proxy** — see `references/fallback-curl-research.md` for the exact
  proxy syntax, API endpoints, and JSON-parsing patterns that work on this
  machine.

## Phase 4: Model Availability Probing (new model releases)

When the user asks "is model X available on platform Y" or "where can I find
free access to model Z" for a **newly released model**, follow the systematic
platform probing workflow in `references/model-availability-research.md`.

Key principle: new models onboard to aggregators in predictable waves —
OpenRouter first (1-2 days), then DeepInfra/NVIDIA NIM (1-4 weeks), then
HuggingFace (after weights upload). Chinese cloud platforms rarely aggregate
foreign models within the first month.

## References
- `references/free-api-directory-2026-07-10.md` — Full verified directory of
  30+ platforms with quotas, rate limits, official links, and selection guide
  (Chinese market focus, bilingual annotations).
- `references/fallback-curl-research.md` — Terminal + curl fallback workflow for
  when web_search/web_extract fail (SOCKS proxy syntax, API endpoints JSON
  parsing, KIMI K3 specific research results).
- `references/model-availability-research.md` — Systematic platform probing
  workflow for new model availability (priority order, curl commands, report
  template, KIMI K3 case study).