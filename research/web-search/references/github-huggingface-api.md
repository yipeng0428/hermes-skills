# GitHub & HuggingFace Programmatic Search

## When to Use

When `web_search` and `web_extract` are unavailable (Firecrawl unconfigured) and you need to:
- Search GitHub for repos, issues, PRs, or code
- Search HuggingFace for models, datasets, or spaces
- Check if a specific model/repo exists and get its metadata

This uses `curl` + the platform REST APIs directly from the terminal.

## GitHub Search

### Search Repositories

```bash
# Basic repo search (sorted by stars)
curl -s "https://api.github.com/search/repositories?q=kimi+k3+gguf&sort=stars&order=desc" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total: {data[\"total_count\"]}')
for r in data.get('items', [])[:10]:
    print(f'{r[\"full_name\"]} ★{r[\"stargazers_count\"]} - {r.get(\"description\",\"\")[:80]}')
"
```

### Search Issues/PRs in a Specific Repo

```bash
curl -s "https://api.github.com/repos/ollama/ollama/issues?q=kimi+k3&sort=created&order=desc&per_page=10" | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    print(f'#{i[\"number\"]} [{i[\"state\"]}] {i[\"title\"][:80]}')
"
```

### Get Organization Repos

```bash
curl -s "https://api.github.com/orgs/moonshotai/repos?per_page=100" | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    print(f'{r[\"name\"]} - {(r.get(\"description\") or \"\")[:80]}')
"
```

### Check if a Repo/Branch Exists

```bash
curl -s "https://api.github.com/repos/MoonshotAI/Kimi" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Name: {d.get(\"full_name\")}')" 2>/dev/null || echo "404 — not found"
```

## HuggingFace Search

### Search Models

```bash
curl -s "https://huggingface.co/api/models?search=kimi+k3&limit=20" | python3 -c "
import sys, json
for m in json.load(sys.stdin):
    print(f'{m[\"id\"]} - downloads: {m.get(\"downloads\",\"N/A\")}')
"
```

### Search by Author

```bash
curl -s "https://huggingface.co/api/models?author=moonshotai&limit=50" | python3 -c "
import sys, json
for m in json.load(sys.stdin):
    print(f'{m[\"id\"]}')"
```

### Check if a Model Exists (via 404 detection)

```bash
curl -s -o /dev/null -w "%{http_code}" "https://huggingface.co/moonshotai/Kimi-K3"
# Returns 404 if not found, 200 if exists
```

### Get Model Metadata

```bash
curl -s "https://huggingface.co/api/models/moonshotai/Kimi-K2.5" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Model: {d[\"id\"]}')
print(f'Downloads: {d.get(\"downloads\")}')
print(f'Tags: {d.get(\"tags\",[])}')
print(f'Created: {d.get(\"createdAt\")}')"
```

## Usage Pattern in a Real Session

When the user asks "find KIMI K3 GGUF/quantization/local deployment":

1. `web_search` fails (Firecrawl unconfigured)
2. Use `web_extract` — also fails (same backend)
3. Pivot to terminal `curl`:
   - Search GitHub repos for kimi k3 gguf/quantization/ollama
   - Check HuggingFace for moonshotai/kimi-k3
   - Check MoonshotAI org repos for any K3-related project
   - Check Ollama issues for K3 support requests
4. Aggregate results into a structured report

## Pitfalls

- **GitHub search syntax** — uses `+` for AND (not `AND`). `repo:user/name` to scope. `sort=stars&order=desc` to rank.
- **GitHub rate limiting** — unauthenticated: 60 req/hour. Authenticated: 5000 req/hour. If you hit 403, wait or use `curl -H "Authorization: token $GITHUB_TOKEN"`.
- **HuggingFace search** — the `search` parameter does substring matching on model ID. `kimi+k3` matches any model containing both terms.
- **HuggingFace 404s** — the API returns `[]` for no matches (not 404). The HTML page returns 404.
- **python3 on Windows** — use `python3 -c "..."` with double quotes. Single quotes fail in MSYS/git-bash.
- **Long outputs** — pipe to `head -20` or `[::10]` slice to avoid flooding context.
- **JSON truncation** — GitHub API truncates large responses (e.g., issue bodies). Use `per_page=30` and limit fields you print.

## Comparison with Other Layers

| Layer | Best For | Limitation |
|-------|---------|------------|
| Firecrawl (1) | General web search | Requires API key |
| GitHub API (terminal) | Repo/issue/PR discovery, metadata | Only GitHub |
| HuggingFace API (terminal) | Model search, download counts, tags | Only HuggingFace |
| Wikimedia API (4) | Factual summaries of entities | Not general search |
| arXiv API (5) | Academic papers | Only arXiv |

## Retrieving Contents from a Known Repo (When Web Tools Fail)

When the user gives you a GitHub URL and `web_search`/`web_extract` are unavailable, use `curl` + GitHub REST API to explore and retrieve contents.

### 1. Get Repo Metadata

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Name: {d[\"full_name\"]}')
print(f'Description: {d.get(\"description\",\"\")}')
print(f'Stars: {d[\"stargazers_count\"]}  Forks: {d[\"forks_count\"]}')
print(f'Default branch: {d[\"default_branch\"]}')
print(f'Language: {d[\"language\"]}')
print(f'Size: {d[\"size\"]} KB')
print(f'License: {d.get(\"license\",{}).get(\"name\",\"None\")}')
print(f'Topics: {d.get(\"topics\",[])}')
print(f'Homepage: {d.get(\"homepage\",\"\")}')
"
```

### 2. Get README Content

```bash
# Via raw.githubusercontent.com (works for any public repo, no auth needed)
curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/README.md"

# Or via API (returns base64-encoded content)
curl -sL "https://api.github.com/repos/OWNER/REPO/readme" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
print(base64.b64decode(d['content']).decode('utf-8'))
"
```

### 3. List File Tree

```bash
# Get recursive file tree (use the actual default branch, not 'main')
curl -sL "https://api.github.com/repos/OWNER/REPO/git/trees/BRANCH?recursive=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for item in d.get('tree', []):
    print(f\"{item['type']:4s} {item['path']}\")
"
```

### 4. Download Methods to Present to User

When the user asks "how do I get this repo's contents", present these options:

| Method | Command | Best For |
|--------|---------|----------|
| **Git clone** | `git clone https://github.com/OWNER/REPO.git` | Full source + version history |
| **Shallow clone** | `git clone --depth 1 https://github.com/OWNER/REPO.git` | Large repos, faster download |
| **Download ZIP** | `curl -L -o repo.zip "https://github.com/OWNER/REPO/archive/refs/heads/BRANCH.zip"` | No git needed, one-shot |
| **Single file** | `curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/to/file"` | Just one file |

> ⚠️ **Default branch may not be `main`** — always check the repo metadata first. Many projects use `master`, `develop`, or versioned branches like `release/v3.8.49`.

### 5. Get Specific File Content

```bash
# Any file in the repo via raw URL
curl -sL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/to/file.py"

# Or via API (for files that aren't in root)
curl -sL "https://api.github.com/repos/OWNER/REPO/contents/path/to/file.py" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
print(base64.b64decode(d['content']).decode('utf-8'))
"
```
