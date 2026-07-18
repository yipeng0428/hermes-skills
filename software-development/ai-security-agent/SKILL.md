---
name: ai-security-agent
trigger:
  - "build an AI security agent"
  - "AI-powered system monitoring"
  - "AI-driven threat detection"
  - "smart antivirus"
  - "intelligent endpoint protection"
  - "security monitoring agent"
  - "detect anomalous processes with ML"
  - "ransomware detection with AI"
  - "local system security dashboard"
  - "automate security response"
  - "process anomaly detection"
  - "real-time threat monitoring agent"
description: >
  Build autonomous AI-powered local system security agents that combine
  rule-based detection, ML anomaly detection (Isolation Forest), behavioral
  ransomware detection, automated response (dry-run → live), and real-time
  web dashboards. Windows + psutil + scikit-learn + Flask.
---

# AI Security Agent Development

Build autonomous, locally-running security agents that combine rules, ML, behavioral analysis, and automated response into a single coherent system.

## When to use

- Replace/extend traditional antivirus with intelligent monitoring
- Process-level anomaly detection using machine learning
- Behavioral ransomware detection (IO pattern analysis)
- Automated threat response with dry-run safety
- Real-time security dashboard for the local machine

## Architecture (5 layers, bottom-up)

```
┌──────────────────────────────────────────────────┐
│  Web Dashboard (Flask, threaded, auto-refresh)    │
├──────────────────────────────────────────────────┤
│  Auto Responder — dry-run first, live after       │
├──────────────────────────────────────────────────┤
│  AI Analyzer (Isolation Forest, 10-dim features)  │
├──────────────────────────────────────────────────┤
│  Rule Engine — baseline risk scoring              │
├──────────────────────────────────────────────────┤
│  Process Monitor (psutil) — live system data      │
└──────────────────────────────────────────────────┘
```

## Implementation phases

### Phase 1: Minimal working agent

```python
import psutil
import logging
import time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent")

def calculate_risk(proc_info):
    risk = 0
    name = (proc_info.get("name") or "").lower()
    if name in ["cmd.exe", "powershell.exe", "bash.exe"]:
        risk += 60
    exe = (proc_info.get("exe") or "").lower()
    if "temp" in exe or "tmp" in exe:
        risk += 30
    return min(risk, 100)

while True:
    metrics = {
        "cpu": psutil.cpu_percent(interval=1),
        "mem": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("C:\\").percent,
        "procs": len(psutil.pids()),
        "net": len(psutil.net_connections()),
    }
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            info = proc.info
            info["risk_score"] = calculate_risk(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    time.sleep(10)
```

Always guard `None` from `proc.info.get(...)` — many kernel processes return `None` for name/exe/user.

### Phase 2: AI analysis engine

**Algorithm:** Isolation Forest — unsupervised, no labeled data needed, fast to retrain online.

**Feature vector (10 dims):**
`[cpu_pct, mem_pct, threads, io_read_KB, io_write_KB, connections, risk_score, is_exe, is_user, threads*cpu]`

**Training recipe (proven in production):**
1. Capture a real-system snapshot of currently-running processes as the "normal" baseline
2. Generate synthetic normal + anomaly samples (see `references/architecture.md`)
3. Combined-fit a `StandardScaler` on real + synthetic data
4. Train IsolationForest with `contamination=0.06` on scaled data
5. Persist model + scaler together via pickle (NOT joblib — pickle handles sklearn objects better)

```python
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

# 1. Collect real normal processes
real_normal = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent',
                                  'num_threads', 'username']):
    try:
        info = proc.info
        name = (info.get('name') or '').lower()
        if name and info.get('username') and 'system' not in str(info.get('username', '')).lower():
            real_normal.append([
                info.get('cpu_percent', 0),
                info.get('memory_percent', 0),
                info.get('num_threads', 1),
                0, 0, 0,
                20 + hash(name) % 30, 1, 1,
                info.get('num_threads', 1) * info.get('cpu_percent', 0)
            ])
    except:
        pass

# 2. Generate synthetic data
synthetic = generate_training_data(150)  # 150 normal + 37 anomaly

# 3. Fit scaler + train
X = np.array(synthetic + real_normal)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    contamination=0.06,   # 6% — Windows produces many legitimate unusual processes
    random_state=42,
    n_estimators=200,
    max_samples=256
)
model.fit(X_scaled)

# 4. Persist together
with open(model_path, 'wb') as f:
    pickle.dump({'model': model, 'scaler': scaler}, f)
```

**Prediction:**
```python
def predict_anomaly(proc_info):
    features = extract_features(proc_info)
    X = np.array([features])
    if scaler:
        X = scaler.transform(X)
    prediction = model.predict(X)[0]  # -1 = anomaly, 1 = normal
    score = model.decision_function(X)[0]
    return {
        "is_anomaly": prediction == -1,
        "anomaly_score": float(score),
        "risk_level": "anomaly" if prediction == -1 else "normal"
    }
```

**Thresholds (tuned for low false-positive rate):**
| decision_function score | risk level |
|------------------------|------------|
| < -0.55                | critical   |
| < -0.35                | high       |
| < -0.15                | medium     |
| ≥ -0.15                | normal     |

Keep contamination at 6-8% — Windows produces many legitimate unusual processes. Going above 10% causes false-positive floods (100+ per scan).

### Phase 3: Auto responder

**Never execute on first run.** Always debut in `dry-run` mode (log suggested actions, do not terminate).

```python
def execute_response(self, threat_info, dry_run=True):
    """Execute auto-response. dry_run=True logs only, dry_run=False executes."""
    risk_level = threat_info.get('risk_level', 'low')
    pid = threat_info.get('pid')
    exe = threat_info.get('exe')
    responses = []
    
    if risk_level == 'critical':
        if dry_run:
            self.logger.critical(f"[建议] 应终止进程 {threat_info.get('name')} PID={pid}")
            responses.append(('terminate_suggested', True))
        else:
            if pid:
                responses.append(('terminate', self.terminate_process(pid)))
            if exe:
                responses.append(('isolate', self.isolate_file(exe)))
    
    elif risk_level == 'high':
        if dry_run:
            self.logger.warning(f"[建议] 应监控 {threat_info.get('name')} PID={pid}")
            responses.append(('monitor_suggested', True))
        else:
            if pid:
                responses.append(('terminate', self.terminate_process(pid)))
    
    else:
        responses.append(('log_only', True))
    
    return {'threat': threat_info.get('name'), 'pid': pid, 'responses': responses}
```

| Risk level | Dry-run action | Live action (after validate) |
|------------|----------------|------------------------------|
| critical   | log "should terminate + isolate" | terminate pid + quarantine exe |
| high       | log "should monitor"             | optionally terminate          |
| medium     | log "record"                     | log only                      |
| low        | ignore                           | ignore                        |

User must explicitly confirm before `dry_run=False`.

### Phase 4: Ransomware detection

Two signals, evaluated per-pid over ≥2-second IO deltas:

1. **IO pattern:** `write_speed > 10 MB/s` AND `write_speed > read_speed × 5` → likely bulk encryption
2. **Name signature:** match name against `encrypt, locky, wannacry, petya, cerber, cryptolocker, teslacrypt, badrabbit`

Track history in `self.io_history[pid] = {rb, wb, t}`. Clean up stale pids periodically.

### Phase 5: Web dashboard

Flask in a daemon `Thread`. Use `<meta http-equiv="refresh" content="10">` for clients — simpler than WebSockets.

Two routes minimum:
- `GET /` → HTML dashboard
- `GET /api/status` → JSON `{cycle, threats, metrics}`

**Common 500 cause:** attribute-name typos in HTML f-strings (`self.agent.ai_analyzer` when the real name is `self.agent.ai`). Always cross-check template references against `__init__`.

## Critical pitfalls

1. **psutil NoneType** — `(proc_info.get('name') or '').lower()` is mandatory. Bare `.lower()` crashes on some system pids.
2. **`connections() → net_connections()`** — psutil ≥7.x renamed it. Use `proc.net_connections()` with fallback.
3. **Isolation Forest contamination too high** → 100+ false alarms per scan. Run 30+ dry-run cycles before trusting results.
4. **Dashboard 500s from attribute typos** → Flask returns 500 silently in production mode. Check every `self.agent.X` in HTML.
5. **Shell escaping in f-strings** — `"` inside HTML attributes breaks Python f-string parsing prematurely. Use single quotes or `&quot;`.
6. **Killing your own shell** — in git-bash/WSL, terminating cmd/bash kills the agent's own parent. Exclude own pid-session, or keep dry-run for interactive terminals.
7. **Terminating system pids (0, 4)** — adding a simple name-based risk model will flag System/Registry. Whitelist pid < 5 and common system processes early.
8. **Portable vs Installer conflict** — When you find a commercial app missing from Program Files but a portable app running (both with HKLM\SOFTWARE\ entries), the portable installer may have overwritten/moved the original installation. Check for `*.BackupBy*Portable` directories to confirm.

## Workflow order

1. Phase 1 (baseline runs) → 2. Phase 3 dry-run (validate detection) → 3. Phase 2 (train AI on real dry-run baseline) → 4. Phase 4 (ransomware) → 5. Phase 5 (dashboard).

Train the AI model *after* you've seen what your own system looks like at baseline — synthetic-only training generalizes poorly to the user's actual process mix.

## Files in this skill

- `references/architecture.md` — complete 5-layer architecture, exact feature vector ranges, training recipe math
- `references/windows-security.md` — Windows Defender coexistence, registry, ETW, safe dry-run practices
- `scripts/train_baseline.py` — runnable snapshot+train script that bootstraps a model from the live system