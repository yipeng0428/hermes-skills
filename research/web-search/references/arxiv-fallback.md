# arXiv Fallback for Web Search

When `web_search` and `web_extract` are unavailable (no Firecrawl API key, no Nous Portal credits), the arXiv REST API is the most powerful free research fallback for academic/scientific topics.

## Why arXiv?

- **Free, no API key required**
- **Rich content**: Full abstracts, paper IDs, author lists, categories, publication dates
- **REST API**: Simple GET requests, returns Atom XML
- **Semantic Scholar integration**: Cross-reference for citation counts, related papers, recommendations

## The Workflow

### Step 1: Search by Keyword

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:KEYWORD1+AND+all:KEYWORD2&max_results=10&sortBy=submittedDate&sortOrder=descending" | uv run python -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns)[:3])
    summary = entry.find('a:summary', ns).text.strip()[:180]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    print(f'{i+1}. [{arxiv_id}] {title}')
    print(f'   Published: {published} | Authors: {authors}...')
    print(f'   Categories: {cats}')
    print(f'   Summary: {summary}...')
    print()
"
```

### Step 2: Fetch Full Abstract for Specific Paper

```bash
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300" | uv run python -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
entry = root.find('a:entry', ns)
print('Title:', entry.find('a:title', ns).text.strip())
print()
print('Abstract:', entry.find('a:summary', ns).text.strip())
"
```

### Step 3: Use Semantic Scholar for Citation Data

```bash
# Get citation count + impact metrics
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,citationCount,influentialCitationCount,year,abstract" | python3 -m json.tool

# Get recommendations for related work
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}' | python3 -m json.tool
```

## Query Syntax Reference

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.AI` |

### Boolean Operators
- **AND**: `all:GPT+OR+all:BERT`
- **OR**: `all:GPT+OR+all:BERT`
- **AND NOT**: `all:language+model+ANDNOT+all:vision`
- **Exact phrase**: `ti:"chain+of+thought"`

## Key Categories for AI Research

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.LG` | Machine Learning |
| `cs.CV` | Computer Vision |
| `cs.MA` | Multi-Agent Systems |
| `cs.RO` | Robotics |
| `stat.ML` | Machine Learning (Statistics) |

## Rate Limits

| API | Rate | Auth |
|-----|------|------|
| arXiv | ~1 req / 3 seconds | None |
| Semantic Scholar | 1 req / second | None (100/sec with key) |

## When to Use This Fallback

- Research surveys and literature reviews
- Finding state-of-the-art methods for a task
- Tracking recent developments in a field
- Cross-referencing claims with academic sources

## When NOT to Use

- Real-time news or recent events (arXiv has publication lag)
- General knowledge queries (use Wikimedia Layer 4 instead)
- Non-academic market data or business intelligence
