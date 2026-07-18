# arXiv REST API Reference

Free API for academic papers and tech topics. No API key required (~1 req/3s rate limit).

## API Endpoint

```
http://export.arxiv.org/api/query?search_query=QUERY&sortBy=SORT&sortOrder=ORDER&max_results=N
```

## Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `search_query` | Search query (see syntax below) | Required |
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` | `relevance` |
| `sortOrder` | `ascending`, `descending` | `descending` |
| `max_results` | 1-30000 | 10 |
| `start` | Offset for pagination | 0 |

## Search Query Syntax

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:"human AI workflow"` |
| `ti:` | Title | `ti:"cognitive augmentation"` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement learning` |
| `cat:` | Category | `cat:cs.AI` |

**Boolean operators**: `+` (AND), `OR`, `ANDNOT`, `"phrase"` (exact match)

## Shell Usage (Windows/MSYS/Git-bash)

```bash
# Latest papers in cs.AI
curl -s --max-time 20 -L "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=6"

# Search by title keywords
curl -s --max-time 20 -L "http://export.arxiv.org/api/query?search_query=ti:%22cognitive+augmentation%22+AND+(all:%22AI%22+OR+all:%22human%22)&sortBy=submittedDate&sortOrder=descending&max_results=5"

# Python urllib bypass proxy (when urllib fails due to MSYS proxy):
# proxy_handler = urllib.request.ProxyHandler({})
# opener = urllib.request.build_opener(proxy_handler)
```

## XML Parsing Template

```python
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for entry in root.findall('a:entry', ns):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns)[:3])
    summary = entry.find('a:summary', ns).text.strip()[:300].replace('\n', ' ')
    print(f'{arxiv_id} [{published}] {title}')
    print(f'   Authors: {authors}')
    print(f'   {summary}')
    print()
```

## Common Categories

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `cs.HC` | Human-Computer Interaction |
| `cs.CR` | Cryptography |
| `stat.ML` | ML (Statistics) |
| `econ.EM` | Econometrics |

## Rate Limits

- ~1 request per 3 seconds
- No authentication required
- Returns Atom XML format

## Notes

- arXiv IDs: old format `hep-th/0601001` vs new `2402.03300`
- Always use versioned URLs for citations: `arXiv:1706.03762v7`
- Withdrawn papers have "withdrawn" in the `<summary>` field
- `export.arxiv.org` may redirect (HTTP 301) — use `curl -L` to follow redirects
