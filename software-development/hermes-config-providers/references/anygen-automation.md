# AnyGen Integration Notes (from 2026-07-12 session)

## What AnyGen is
AI content-generation SaaS (slides/docs/diagrams/websites/images/research).
NOT a chat-completion API. Driven by the official `@anygen/cli` or the web UI.

## API keys (user has 3 accounts)
Format: `sk-ag-<base64-ish>` — these are OPENCLAW/agent keys, set via
`ANYGEN_API_KEY` env var or `anygen auth login --api-key sk-xxx`.
- Account 1: Google OAuth login
- Account 2: Lark (feishu) QR-code scan login
- Account 3: (third key, login method unconfirmed)

## CLI
```
npm install -g @anygen/cli
export ANYGEN_API_KEY=sk-ag-...
anygen task create --data '{"operation":"slide","prompt":"..."}'
anygen task get --params '{"task_id":"xxx"}' --wait
anygen task +download --task-id <id> --output-dir ./out
```
Resources: only `file` and `task`. **No credit/points/checkin command exists.**

## API surface discovered
- Base: `https://www.anygen.io/v1/openapi/...`
- `POST /v1/openapi/tasks` — create generation task
- `GET  /v1/openapi/tasks/:task_id` — poll status
- Auth: `Authorization: Bearer sk-ag-...`
- Guessed paths (`/user/credits`, `/checkin`, `/daily-checkin`, etc.) all return
  the SPA HTML shell (200 but not JSON) — they are frontend routes, NOT real APIs.

## Daily 300-credit claim — UNRESOLVED
The "claim 300 points daily" action is a **web-UI button** (needs login).
No API endpoint found. To automate:
1. Log in (Google / Lark QR — can't be headless), OR
2. User manually clicks claim once + capture the XHR with Puppeteer
   `page.on('response')` -> replicate via script + cron.

## Browser automation setup that worked (Windows)
- Puppeteer installed in `/tmp/anygen-automation/` (or any workdir)
- Chrome at `C:/Users/win10/.cache/puppeteer/chrome/win64-150.0.7871.24/chrome-win64/chrome.exe`
- `userAuth` in the page's `window.User` shows `userType:"guest"` when not logged in
  -> no credit API calls fire until authenticated.

## Status
- Puppeteer+Chrome installed, AnyGen CLI installed
- API key format & base URL identified
- Daily-credit automation BLOCKED on capturing the real claim request
  (needs a logged-in session — user to provide the XHR, or run non-headless Chrome)
