---
name: hermes-plugin-patterns
description: Advanced patterns for Hermes desktop plugins — iframe backends, connection state, cross-skill quirks.
version: 1.0.0
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [desktop, plugins, patterns, ui]
    category: productivity
    related_skills: [hermes-desktop-plugins, notion]
---

# Hermes Plugin Patterns

Production-tested patterns and pitfalls for building Hermes desktop plugins.
Extends `hermes-desktop-plugins` (API reference) with real-world implementation
knowledge. Load this alongside `hermes-desktop-plugins` when building complex
plugin UIs.

## When to Use

- Building a dashboard, data panel, or any plugin with significant UI complexity
- The plugin needs to call external APIs (Notion, databases, local services)
- You want the plugin UI to work both inside Hermes AND as a standalone window
- The plugin's data layer is too heavy for raw `jsx()` components

## Pattern 1: iframe + Local Python Backend

For complex UIs, embed an iframe pointing to a local web server instead of
building everything in React components. The plugin handles connection state;
the backend handles all data logic.

### Architecture

```
┌─────────────────────────────────┐
│   Hermes Desktop App            │
│  ┌───────────────────────────┐  │
│  │  Plugin (plugin.js)        │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ iframe → localhost   │  │  │
│  │  │  port               │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Python Backend (Flask)         │
│  localhost:8765                 │
│  • API routes (/api/...)        │
│  • Notion/DB integration        │
│  • Static file serving (HTML)   │
└─────────────────────────────────┘
```

### Plugin shell structure

The plugin.js has three states:

1. **Checking** — initial connection test, show spinner
2. **Offline** — backend unreachable, show startup prompt with retry button
3. **Online** — render iframe

```javascript
// Key imports
import { useState, useEffect, useRef } from 'react';
import { jsx, jsxs } from 'react/jsx-runtime';
import { host, Button, GlyphSpinner } from '@hermes/plugin-sdk';

// Custom fetch with timeout (AbortSignal.timeout not universally available)
function fetchWithTimeout(url, options = {}, timeout = 3000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(timer));
}
```

### Pane registration

```javascript
ctx.register({
  id: 'my-panel',
  area: 'panes',
  render: () => jsx(MyComponent, {}),
  data: {
    placement: 'right',   // or 'left', 'bottom', 'main'
    title: 'My Panel',
    width: '420px',
    height: '520px',
  },
});
```

### Frontend independence

The HTML/CSS/JS frontend is a standalone web page served by the Python backend.
It can be opened directly in a browser for development and testing, AND loaded
via iframe in the Hermes plugin. This means:

- Develop and debug the UI in a browser first (DevTools, hot reload)
- The plugin is a thin shell — just the iframe + connection management
- The same frontend can be opened as a standalone floating window (via a .bat
  script that starts the backend + opens the browser)

### Backend startup

Provide a `.bat` launcher on the user's Desktop:

```bat
@echo off
cd /d "path\to\backend"
start "Backend" /MIN python server.py
timeout /t 3 /nobreak >nul
start http://localhost:8765
```

The plugin can optionally offer a "Launch Backend" button that calls
`host.request(...)` to execute the startup command — but note that
`host.request('terminal.exec', ...)` may not exist on all Hermes versions.
Treat it as a best-effort convenience, not a critical path.

## Pitfalls

### AbortSignal.timeout() not available

The Hermes desktop app's rendering environment may not support
`AbortSignal.timeout(ms)`. Use a wrapper:

```javascript
function fetchWithTimeout(url, options = {}, timeout = 3000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(timer));
}
```

### Closure over stale state in intervals

When using `setInterval` to retry connections, the callback captures the state
at creation time. Use a `useRef` to always read the latest value:

```javascript
const onlineRef = useRef(false);
useEffect(() => { onlineRef.current = online; }, [online]);

useEffect(() => {
  const timer = setInterval(() => {
    if (!onlineRef.current) check();  // reads latest, not closure value
  }, 5000);
  return () => clearInterval(timer);
}, []);  // empty deps — interval set once
```

### `host.request('terminal.exec', ...)` may not exist

The gateway RPC surface varies by Hermes desktop app version. Don't rely on
specific RPC methods for critical plugin functionality. Use them as optional
convenience features with fallback UI.

### iframe sandbox

Set `sandbox="allow-scripts allow-same-origin allow-forms allow-popups"` on
the iframe to allow the frontend to function while maintaining security.
`allow-same-origin` is required for the frontend's fetch() calls back to the
backend on the same origin.

## Cross-Skill Notes

### Notion data_source_id quirk

When a Notion database has relations to other databases, the `/search` endpoint
may return **two** `data_source` entries with the same `database_id` but
different `data_source_id` values. One has the real title; the other may have
an empty title (auto-generated from the relation). When querying, **test both**
— one may return 400 while the other works fine.

Example from production:
- `39e86cdd-...` (title "万凯收件箱") → 400 on query with valid filter
- `58324c59-...` (empty title, relation-generated) → worked correctly

**Rule**: always verify queries against both data_source_ids before assuming
the filter or query format is wrong. See `references/notion-datasource-quirk.md`
for the full reproduction recipe.

### Checkbox filter format (Notion API v2025-09-03)

Confirmed working:
```json
{"filter": {"property": "已转入", "checkbox": {"equals": false}}}
```

Use `false`/`true` (JSON boolean), not strings.

### Date range filter for weekly reports

```json
{
  "filter": {
    "and": [
      {"property": "日期", "date": {"on_or_after": "2026-07-13"}},
      {"property": "日期", "date": {"on_or_before": "2026-07-19"}}
    ]
  }
}
```

## Verification

- Plugin appears in Hermes after **Reload desktop plugins** (⌘K)
- Backend health check: `curl -s http://localhost:8765/api/health` returns `{"status":"ok"}`
- Frontend loads in browser independently from Hermes
- Connection state transitions: checking → online (iframe visible) or offline (retry prompt)
