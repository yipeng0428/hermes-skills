# Real-Session Notion AI Monitor Implementation Notes (2026-07-13)

## What the skill SKILL.md describes vs. what actually ships

The Notion AI Monitor SKILL.md **describes** a `monitor_simple.py` but **does not include it** as a skill file.
When the user asks to run the monitor, you must **write the script from scratch**.
Place it at `~/.hermes/notion-ai-monitor/monitor_simple.py` (the skill's canonical project location, not inside the skill directory itself).

## Known real-world testing results

| Source | HTTP Status | Notes |
|--------|-------------|-------|
| Notion Blog (`notion.so/blog`) | 200 OK | Contains "Notion AI" in body — high false-positive rate |
| Notion Help (`notion.so/help`) | 200 OK | Contains "Notion AI" in body — high false-positive rate |
| Notion Pricing (`notion.so/pricing`) | 200 OK | Contains "Notion AI" in body — high false-positive rate |
| Notion What's New (`notion.so/whats-new`) | 401 | Requires JS/auth; direct HTTP fetch fails |
| Reddit `r/Notion` + `r/NotionAI` (`.json` endpoint) | 403 | Reddit blocks via User-Agent; needs OAuth or pushshift-like workaround |
| Product Hunt (`producthunt.com/search?q=notion+ai`) | 200 OK | Works; adds noise but can surface real deals |
| Web search (`web_search` tool) | May fail | Requires Nous Portal Firecrawl credits; unavailable when credits exhausted |

## Scoring logic fix needed

The naive approach detects the literal keyword "Notion AI" anywhere on a page — this triggers every time on any Notion page because every page contains "Notion AI" in the footer/navigation.

**Real discount detection** requires parsing for specific patterns:
- "free trial", "coupon code", "discount code", "promo code", "giveaway"
- "student plan", "education discount", "educator pricing"
- "plus plan", "ai add-on", "monthly/annual"
- "referral", "invite link"

**Without semantic/regex patterns, the monitor returns false positives. Always filter for discount-type language, not just brand mentions.**

## Dependencies on this host machine

All present as of 2026-07-13:
- `yaml` (PyYAML) ✅
- `requests` ✅
- `beautifulsoup4` ✅
- `schedule` ✅

No additional installs needed.

## File layout convention

```
~/.hermes/notion-ai-monitor/
├── config.yaml          — monitoring config (scoring weights, keywords, social media toggles)
├── monitor_simple.py    — the actual runnable script (you must create this)
├── monitor.log          — auto-generated execution log
└── monitor_results.jsonl — auto-generated JSONL of found opportunities
```
