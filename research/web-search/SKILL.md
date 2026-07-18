---
name: web-search
description: "Hermes web search redundancy: configure Firecrawl, Google Programmable Search, and DuckDuckGo fallbacks so search never silently fails."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, search, firecrawl, google, duckduckgo, redundancy, china]
---

# Web Search Redundancy

## Trigger Conditions

- `web_search` tool returns "Web tools are not configured. Set FIRECRAWL_API_KEY..."
- Nous Portal credits exhausted, managed Firecrawl unavailable
- User in China and wants resilient search independent of Nous billing state
- Any session where search failure is unacceptable and a fallback is needed

## Background

Hermes `web_search` / `web_extract` tools use **Firecrawl** as the sole backend
(`config.yaml → web.backend: firecrawl`). There is no plugin point to swap in
another search provider while keeping the same tool name.

Firecrawl requires either:
- `FIRECRAWL_API_KEY` — cloud Firecrawl (paid via Nous Portal credits)
- `FIRECRAWL_API_URL` — self-hosted Firecrawl instance

When neither is configured, **both `web_search` and `web_extract` fail silently**
with "Web tools are not configured".

This skill documents the fallback strategy:

| Layer | Tool | Cost | Requires | Reliability |
|-------|------|------|----------|-------------|
| 1 (primary) | Firecrawl via `web_search` | Nous credits | `FIRECRAWL_API_KEY` or `FIRECRAWL_API_URL` | High when funded |
| 2 | Google Programmable Search API via `execute_code` | 100 queries/day free | `GOOGLE_API_KEY` + Search CX | High |
| 3 | DuckDuckGo HTML scrape via `execute_code` | Free | None | Medium (rate-limited) |
| 4 (factual fallback) | **Wikimedia REST API** via `execute_code` | Free | None | High (for factual summaries) |
| 5 (research fallback) | **arXiv REST API** via `terminal` (curl + Python) | Free | `curl`, Python | High (academic papers) |
| 6 (code/model fallback) | **GitHub & HuggingFace APIs** via `terminal` (curl + Python) | Free | `curl`, Python | High (repos, issues, models) |

- **Layer 4** (Wikimedia) is NOT a general web search — it's a structured factual source for company/technology/concept summaries when Layers 1-3 are unavailable.
- **Layer 5** (arXiv) is for academic/scientific research. Use `curl + python3` in terminal (NOT `execute_code`) to query + parse XML — avoids MSYS proxy issues.
- **Layer 6** (GitHub/HuggingFace) is for searching repositories, issues, PRs, and ML models when web search is unavailable. Use `curl + python3` in terminal.

## Setup

### Layer 1 — Firecrawl (Hermes native)

```bash
# Cloud (via Nous Portal credits)
hermes config set web.backend firecrawl
echo "FIRECRAWL_API_KEY=fc-..." >> "$HERMES_HOME/.env"

# Self-hosted
hermes config set web.backend firecrawl
echo "FIRECRAWL_API_URL=http://localhost:3000" >> "$HERMES_HOME/.env"
```

Restart Hermes after any `.env` change.

### Layer 2 — Google Programmable Search API (free tier)

1. Go to https://programmablesearchengine.google.com/ — create a search engine
   (set "Sites to search" to `*.com` for web-wide).
2. Copy the **Search engine ID (CX)**.
3. Go to https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   — enable the Custom Search API.
4. Go to Credentials → Create API key → copy the key.
5. Add to Hermes `.env`:

```bash
echo "GOOGLE_API_KEY=AIza..." >> "$HERMES_HOME/.env"
echo "GOOGLE_SEARCH_CX=your-cx-here" >> "$HERMES_HOME/.env"
```

### Layer 3 — DuckDuckGo HTML (no registration)

No setup needed. Call `execute_code` to run the fallback script in
`scripts/ddg_search.py`. Handles rate-limiting with exponential backoff
(1 s → 2 s → 4 s).

> ⚠️ **CAPTCHA Reality (2025-2026)**: DDG HTML endpoint (`html.duckduckgo.com`)
> is now heavily CAPTCHA-protected for programmatic requests. 60-80% of
> curl/Python requests trigger an image-based CAPTCHA challenge ("select all
> squares containing a duck") which scripts cannot solve.
> 
> **When DDG returns CAPTCHA, skip straight to Layer 4 (Wikimedia API)**
> rather than retrying — backoff will not unblock it. For factual entity
> summaries and tech topics, Layer 4 is faster and more reliable than fighting
> DDG.
> 
> **Typical failure signature**:
> ```
> Please complete the following challenge to confirm this search was made by a human.
> Select all squares containing a duck:
> Code: d4cd0dabcf4caa22ad92fab40844c786
> ```
> When you see this pattern, immediately pivot to Layer 4 or arxiv Layer 5.

### Layer 5 — arXiv API (academic/specialized topics)

For research papers, tech topics, or domain-specific academic content, arXiv
operates a free REST API (no key, ~1 req/3s). **Works via shell `curl` even
when Python `urllib` fails** because curl inherits the MSYS proxy env vars.

```bash
# Via shell curl (preferred — proxy-friendly)
curl -s --max-time 20 -L "http://export.arxiv.org/api/query?search_query=all:%22human+AI+workflow%22&sortBy=submittedDate&sortOrder=descending&max_results=6"

# Parse XML output in Python
curl -s ... | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for entry in root.findall('a:entry', ns):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    print(f'{arxiv_id}: {title}')
"
```

> ⚠️ **Python `urllib` + MSYS proxy issue**: On Windows/Git-bash environments,
> `urllib.request` does NOT inherit `http_proxy`/`https_proxy` env vars the
> way curl does. If you must use Python directly, explicitly bypass the proxy:
> ```python
> proxy_handler = urllib.request.ProxyHandler({})
> opener = urllib.request.build_opener(proxy_handler)
> req = urllib.request.Request(url, headers={'User-Agent': 'HermesAgent/1.0'})
> with opener.open(req, timeout=25) as resp:
>     data = resp.read().decode('utf-8')
> ```
> Or use shell `curl` and pipe to Python for parsing — more reliable.

### Layer 4 — Wikimedia REST API (no registration, factual summaries)

No setup needed. Use when you need **factual summaries** of companies, technologies,
concepts, people — not general web search. Works even when DDG is rate-limited.

Call pattern in `execute_code`:

```python
import urllib.request, json, re

def wiki_summary(title, lang="en"):
    """Fetch a plain-text extract from Wikipedia via the REST API."""
    url = (
        f"https://{lang}.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(title)}"
        f"&prop=extracts&exintro=true&explaintext=true&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "HermesAgent-Research/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    for page in data.get("query", {}).get("pages", {}).values():
        extract = re.sub(r"\s+", " ", page.get("extract", "")).strip()
        if "may refer to" in extract:
            return None  # disambiguation page
        return extract
    return None
```

**Key behaviors**:
- Returns ~300-800 character plain-text intros — enough for company/technology profiling.
- Returns `None` for disambiguation pages; try a more specific title (e.g., "IonQ" → "IonQ" works, but "Astra" → try "Astra (American spaceflight company)").
- Supports `zh.wikipedia.org` for Chinese topics.
- Much more stable than DDG for factual queries — no CAPTCHA, no aggressive rate-limiting (but still sleep ~0.5s between calls as courtesy).

## Usage Pattern

When the built-in `web_search` fails, run this sequence in `execute_code`:

```
import hermes_tools
# 1. Try Firecrawl via the tool (Hermes handles this natively)
# 2. If that fails, call the Google helper
# 3. If that fails, call the DDG helper
# 4. If you need factual summaries of specific entities, call wiki_summary()
```

Both helper functions are available in `scripts/search_helpers.py`:
- `google_search(query, api_key, cx, num=5)` — returns list of {title, url, snippet}
- `ddg_search(query)` — returns list of {title, url, snippet}

For factual entity summaries, call `wiki_summary(title, lang="en")` directly in your script.

## Execution Flow (recommended)

1. Try Firecrawl via `web_search` tool (Hermes handles this natively)
2. If Firecrawl fails, try Google Programmable Search
3. If Google fails/unavailable, try DDG HTML
4. **If DDG returns CAPTCHA → skip straight to Wikimedia (Layer 4)**
5. For academic/tech topics, try arXiv shell curl (Layer 5)
6. **For code repos, issues, or ML models, use GitHub/HuggingFace API (Layer 6)**

## China-Specific Notes

- Google API is accessible via the same 快柠檬 VPN port (`127.0.0.1:10793`)
  already configured for Nous Portal — no additional proxy setup needed.
- DDG HTML endpoint `https://html.duckduckgo.com/html` is usually reachable
  from China without VPN, but results may be region-skewed.
- **Wikimedia API works from China without VPN** for both en.wikipedia.org and zh.wikipedia.org — reliable fallback.
- If both Google and DDG are slow, the DDG script retries automatically;
  do not spawn parallel calls — sequential fallback is simpler to debug.

## Pitfalls

- **DDG returns CAPTCHA, not results** — When `html.duckduckgo.com` triggers the "select all squares containing a duck" page, abandon DDG immediately. Pivot to Layer 4 (Wikimedia API) or Layer 5 (arXiv). Backoff will not unblock.
- **Python urllib + MSYS proxy on Windows** — `urllib.request` does not inherit `http_proxy`/`https_proxy` env vars like curl does. Either use shell `curl` (inherits env) or explicitly bypass the proxy via `ProxyHandler({})`.
- **arXiv via Python urllib silently fails** — The arXiv API (`export.arxiv.org`) returns HTTP 301 + empty body when proxied through MSYS. Use `curl -s -L` and pipe to Python for parsing — more reliable on Windows.
- **GitHub API rate limiting** — Unauthenticated: 60 req/hour. Authenticated: 5000 req/hour. If you hit 403, wait or use `curl -H "Authorization: token $GITHUB_TOKEN"`.
- **GitHub search syntax** — Uses `+` for AND (not `AND`). `repo:user/name` to scope. `sort=stars&order=desc` to rank.
- **HuggingFace search** — The `search` parameter does substring matching on model ID. `kimi+k3` matches any model containing both terms. Returns `[]` for no matches (not 404).
- **Do not put the same API key in multiple services** — keep Google key in `.env` only; do not leak it to notebooks or configs checked into git.
- **`.env` changes require a full restart** — Hermes reads `.env` at process start; mid-session edits are ignored.
- **Firecrawl fallback hides the error** — when Firecrawl is unconfigured the tool returns a generic "not configured" message; do not retry it more than once before jumping to Google.
- **Google free tier is 100 queries/day** — track usage if this is a daily workflow; beyond that the API returns 429.
- **`web_extract` also fails when Firecrawl is unconfigured** — the same "Web tools are not configured" error applies. Use shell `curl` + Python parsing, or use Wikimedia API for factual summaries.

## Files

- `scripts/search_helpers.py` — `google_search()` + `ddg_search()` helpers
- `scripts/ddg_search.py` — standalone DDG fallback (no imports needed)
- `references/google-pse-setup.md` — step-by-step PSE + API key creation
- `references/ddg-search.md` — DDG HTML scraping notes
- `references/wikimedia-api.md` — Wikimedia REST API usage for factual entity summaries
- `references/arxiv-api.md` — arXiv REST API (shell curl + Python parsing) for academic/tech topics
- `references/github-huggingface-api.md` — GitHub & HuggingFace REST API for repo/issue/model search, plus **retrieving repo contents** (metadata, README, file tree, download methods) when web tools fail