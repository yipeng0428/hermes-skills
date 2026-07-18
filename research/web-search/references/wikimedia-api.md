# Wikimedia REST API — Factual Entity Summaries

## When to Use

Use the Wikimedia REST API when:
- Firecrawl, Google Programmable Search, and DuckDuckGo are all unavailable or rate-limited
- You need **factual summaries** of specific named entities (companies, technologies, concepts, people, places)
- You need Chinese-language summaries (zh.wikipedia.org)
- You cannot use `web_extract` because Firecrawl is unconfigured

## API Endpoint

```
https://{lang}.wikipedia.org/w/api.php
  ?action=query
  &titles={URL-encoded title}
  &prop=extracts
  &exintro=true       # only the introduction section
  &explaintext=true   # plain text, no HTML
  &format=json
```

## Python Implementation

```python
import urllib.request
import urllib.parse
import json
import re

def wiki_summary(title, lang="en"):
    """
    Fetch a plain-text extract from Wikipedia via the REST API.
    
    Returns:
        str: ~300-800 character plain-text introduction, or None if not found / disambiguation
    """
    url = (
        f"https://{lang}.wikipedia.org/w/api.php"
        f"?action=query&titles={urllib.parse.quote(title)}"
        f"&prop=extracts&exintro=true&explaintext=true&format=json"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "HermesAgent-Research/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    for page in data.get("query", {}).get("pages", {}).values():
        extract = re.sub(r"\s+", " ", page.get("extract", "")).strip()
        # Disambiguation pages return "Foo may refer to:"
        if "may refer to" in extract:
            return None
        return extract
    return None


def wiki_search_with_fallback(titles, lang="en"):
    """
    Try a list of titles in order; return the first valid summary.
    
    Example: wiki_search_with_fallback(["Astra", "Astra Space", "Astra (American spaceflight company)"])
    """
    for title in titles:
        result = wiki_summary(title, lang)
        if result:
            return title, result
    return None, None
```

## Examples

```python
# English summary
print(wiki_summary("IonQ"))
# "IonQ, Inc. is an American quantum computing hardware and software company..."

# Chinese summary (fallback if en fails)
print(wiki_summary("量子计算", lang="zh"))
# "量子计算是一种遵循量子力学规律调控量子信息单元进行计算的新型计算模式..."

# Handling ambiguous terms
title, summary = wiki_search_with_fallback(["Astra", "Astra Space", "Astra (American spaceflight company)"])
```

## Chinese Usage

- Use `lang="zh"` to query `zh.wikipedia.org`
- Chinese search titles may need to be more specific (e.g., "阿里巴巴集团" instead of "阿里巴巴")
- The Chinese API has the same rate-limit tolerance but 0.5s courtesy sleep still applies

## Rate Limiting & Etiquette

- **No hard rate limit** for casual use (~10+ queries/min recommended max)
- Set `User-Agent: HermesAgent-Research/1.0` (or similar) — Wikimedia may block generic user agents
- If you hit `429 Too Many Requests`, back off 2-5 seconds and retry
- ~~Sleep 0.5s between calls~~ courtesy when doing multi-query scripts

## Limitations

- **NOT a general web search** — only works for entities with Wikipedia pages
- **No real-time data** — prices, recent events, private company financials may be outdated
- **No opinions/analysis** — encyclopedic summaries only
- **Varies by language** — zh.wikipedia.org articles may be significantly different from en.wikipedia.org
- **Disambiguation pages** — returns `None`; use `wiki_search_with_fallback()` with more specific titles

## Comparison with Other Layers

| Layer | Best For | Limitation |
|-------|---------|------------|
| Firecrawl (1) | Full web pages, PDFs | Requires API key |
| Google PSE (2) | General web search | 100 queries/day |
| DuckDuckGo (3) | General web search, no API key | Rate-limited |
| **Wikimedia API (4)** | **Factual summaries of known entities** | **Not general search** |
