#!/usr/bin/env python3
"""
train_baseline.py — Capture live system snapshot and train Isolation Forest model.

Usage:
    python train_baseline.py [--output models/security_model.pkl] [--include-malware-samples] [--contamination 0.06]
    
Output:
    — Trained model + scaler at the given path (default: models/security_model.pkl)
    — Prints training summary and baseline stats
    
Test mode:
    python train_baseline.py --test   # Train on synthetic-only, skip live capture
"""

import psutil
import numpy as np
import pickle
import os
import sys
import time
from datetime import datetime

def capture_baseline(snapshot_seconds=5):
    """Capture running process baseline from the live system."""
    print(f"[baseline] Capturing processes over {snapshot_seconds}s...")
    
    # Warm up
    for p in psutil.process_iter(): pass
    time.sleep(0.5)
    
    baseline = []
    seen_pids = set()
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent',
                                      'num_threads', 'username', 'exe']):
        try:
            info = proc.info
            pid = info['pid']
            if pid in seen_pids or pid < 5:
                continue
            seen_pids.add(pid)
            
            name = (info.get('name') or '').lower()
            if not name:
                continue
            
            # Skip obvious non-processable entries
            if name in ['system idle process']:
                continue
            
            features = [
                info.get('cpu_percent', 0),
                info.get('memory_percent', 0),
                info.get('num_threads', 1),
                0, 0, 0,
                20 + hash(name) % 30,
                1 if name.endswith('.exe') else 0,
                1 if info.get('username') and 'system' not in str(info.get('username')).lower() else 0,
                info.get('num_threads', 1) * info.get('cpu_percent', 0)
            ]
            baseline.append(features)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"[baseline] ✓ {len(baseline)} processes captured")
    return np.array(baseline)


def generate_synthetic(n_normal=150, n_anomaly=37):
    """Generate synthetic training samples."""
    np.random.seed(42)
    
    normal = np.column_stack([
        np.random.uniform(1, 16, n_normal),
        np.random.uniform(5, 35, n_normal),
        np.random.uniform(4, 25, n_normal),
        np.random.uniform(0.1, 5, n_normal),
        np.random.uniform(0.01, 1, n_normal),
        np.random.uniform(1, 8, n_normal),
        np.random.uniform(10, 40, n_normal),
        np.ones(n_normal),
        np.ones(n_normal),
        np.random.uniform(5, 20, n_normal)
    ])
    
    anomaly = np.column_stack([
        np.random.uniform(50, 90, n_anomaly),
        np.random.uniform(40, 80, n_anomaly),
        np.random.uniform(60, 250, n_anomaly),
        np.random.uniform(50, 250, n_anomaly),
        np.random.uniform(20, 100, n_anomaly),
        np.random.uniform(50, 200, n_anomaly),
        np.random.uniform(60, 90, n_anomaly),
        np.ones(n_anomaly),
        np.ones(n_anomaly),
        np.random.uniform(100, 400, n_anomaly)
    ])
    
    return np.vstack([normal, anomaly])


def train(baseline_data, output_path, contamination=0.06):
    """Train IsolationForest on combined data."""
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    
    synthetic = generate_synthetic()
    X = np.vstack([synthetic, baseline_data]) if len(baseline_data) > 0 else synthetic
    
    print(f"[train] Combined {len(X)} samples ({len(synthetic)} synthetic + {len(baseline_data)} live)")
    
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)
    
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=200,
        max_samples=min(256, len(X))
    )
    model.fit(X_s)
    
    # Validate
    train_preds = model.predict(X_s)
    anomaly_frac = (train_preds == -1).mean()
    print(f"[train] Anomaly fraction in training set: {anomaly_frac:.1%}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler}, f)
    
    size = os.path.getsize(output_path)
    print(f"[train] ✓ Saved to {output_path} ({size} bytes)")
    return model, scaler


def quick_test(model, scaler):
    """Quick smoke test with some obvious anomalies."""
    test_procs = [
        [5, 20, 8, 1, 0.5, 3, 25, 1, 1, 40],      # normal
        [95, 85, 200, 200, 80, 150, 80, 1, 1, 19000], # anomaly
        [3, 30, 15, 0.5, 0.1, 2, 20, 1, 1, 45],     # normal
    ]
    
    X = scaler.transform(np.array(test_procs))
    preds = model.predict(X)
    scores = model.decision_function(X)
    
    print("\n[smoke test]")
    for i, (p, pred, score) in enumerate(zip(test_procs, preds, scores)):
        label = "ANOMALY ⚠️" if pred == -1 else "normal ✓"
        print(f"  sample {i+1}: score={score:.3f} → {label}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='models/security_model.pkl')
    parser.add_argument('--contamination', type=float, default=0.06)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    
    print(f"=== AI Security Agent Training ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
    
    if args.test:
        baseline = np.array([]).reshape(0, 10)
        print("[mode] test — synthetic only")
    else:
        baseline = capture_baseline()
    
    model, scaler = train(baseline, args.output, args.contamination)
    quick_test(model, scaler)
    
    print("\n=== Done ===")
    return model, scaler


if __name__ == "__main__":
    main()
