# AI Security Agent Architecture

## Five-layer architecture diagram

```
┌─────────────────────────────────────────────────────────────┐
│                              Web                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Flask Server (port 5000, daemon thread, shared DB)  │    │
│  │  / → HTML dashboard (auto-refresh 10s)               │    │
│  │  /api/status → JSON {cycle, threats, metrics}        │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                         Auto Response                        │
│  ┌───────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ Terminator │  │ File Quarant │  │   Net Blocker     │    │
│  │  proc.kill │  │  mv to dir   │  │  netsh advfirewall│    │
│  └───────────┘  └──────────────┘  └───────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                           AI Engine                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Isolation Forest (unsupervised)                     │    │
│  │  10-dim feature vector → StandardScaler → model      │    │
│  │  decision_function → risk_level mapping              │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                        Rule Engine                           │
│  ┌───────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ Risk Score │  │  Blacklist   │  │     Whitelist      │    │
│  │ 0-100 pts  │  │  name match  │  │  name match → 0   │    │
│  └───────────┘  └──────────────┘  └───────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                          Monitor                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  psutil: process_iter, net_connections,              │    │
│  │  cpu_percent, virtual_memory, disk_usage            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Feature vector (10 dimensions)

| Index | Feature | Shape | Normal range | Anomaly range | Source |
|-------|---------|-------|--------------|---------------|--------|
| 0 | cpu_pct | 0-100 | 1-20 | 50-95 | proc.cpu_percent() |
| 1 | mem_pct | 0-100 | 5-40 | 40-90 | proc.memory_percent() |
| 2 | threads | 1-300 | 4-25 | 60-300 | proc.num_threads() |
| 3 | io_read_KB | MB | 0.1-5 | 50-250 | proc.io_counters() |
| 4 | io_write_KB | MB | 0.01-1 | 20-100 | proc.io_counters() |
| 5 | connections | count | 1-8 | 50-250 | proc.net_connections() |
| 6 | risk_score | 0-100 | 10-40 | 60-95 | rule engine |
| 7 | is_exe | 0/1 | 1 | 1 | name ends .exe |
| 8 | is_user | 0/1 | 1 | 1 | username != system |
| 9 | thread×cpu | product | 5-20 | 200-500 | composite |

## Training data recipe

```
Total: ~350 samples
├── 150 synthetic normal (cpu 1-20, mem 5-40, threads 5-25)
├── 37  synthetic anomaly (cpu 50-90, mem 40-80, threads 50-300)
└── ~160 real processes from psutil snapshot (seed normal baseline)
```

**Scaler:** `StandardScaler()` fit on combined data, persisted with model.

**Model params:**
- `IsolationForest(contamination=0.06, n_estimators=200, max_samples=256, random_state=42)`
- Use `max_samples=256` cap to avoid memory blow-up on systems with 300+ processes.

**Risk level mapping (decision_function output):**
| Score | Level | Meaning |
|-------|-------|---------|
| < -0.55 | critical | almost certainly anomalous |
| < -0.35 | high | clearly above noise floor |
| < -0.15 | medium | borderline, monitor |
| ≥ -0.15 | normal | fits baseline |

## Response action table

| Level | Dry-run | Live (enabled after validation) |
|----|---------|---------------------------------|
| critical | log "should terminate + isolate" | terminate_pid + quarantine_file |
| high | log "should monitor" | log or terminate (configurable) |
| medium | log "record" | log only |
| low | ignore | ignore |

## Ransomware detection rules

**Rule 1: IO pattern (real-time)**
- Compute `(write_bytes_now - write_bytes_prev) / dt` per pid
- If `write_speed > 10 MB/s` AND `write_speed > read_speed × 5` → flag
- Minimum dt: 2 seconds (avoids burst false positives)

**Rule 2: Process name signature**
Match name against: `encrypt, locky, wannacry, petya, cerber, cryptolocker, teslacrypt, badrabbit, locked, vault, ransom`

**Rule 3: File extension scan (optional)**
Check temp dirs and user docs for extensions: `.encrypted`, `.locked`, `.crypt`, `.cerber`, `.aes`, `.ecc`, `.exx`, `.vault`, `.zzz`, `.xyz`, `.aaa`

## Minimum test regime before enabling live response

1. ≥50 dry-run scan cycles
2. False positive rate ≤10% on the user's actual workload
3. Zero false positives for the user's design tools, browsers, chat apps
4. Confirmed detection of at least one test "threat" (e.g. running a CPU spinner script)

Live mode is enabled only after all four checks pass.

## Memory-per-process attribution

The agent's own psutil scanning and Flask server will show up as a python.exe with:
- Moderate CPU (~10-25% briefly during scanning)
- Growing memory (psutil caches small per-process objects)
- Many net_connections in TIME_WAIT (Flask polling, subprocess calls)

The agent should be whitelisted against its own self to avoid recursive termination.

## Disk layout

```
C:\APSA-Mini\               ← project root
├── main.py                 ← minimal v1
├── enhanced_agent.py       ← full v2
├── apsa_v2.log             ← runtime log (rotated)
├── security_model_v2.pkl   ← trained model (rewritten on retrain)
├── models\
│   └── baseline_snapshot.pkl   ← optional: frozen baseline
├── SecurityQuarantine\    ← dry-run only unless live enabled
└── web_templates\         ← optional: external HTML templates
```

Disk usage: ~5-10 MB for the agent + model. Log files grow ~5 MB/day at 5s scan intervals; implement logrotate or truncate when >50 MB.
