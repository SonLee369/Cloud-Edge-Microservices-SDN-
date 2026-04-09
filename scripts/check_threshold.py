#!/usr/bin/env python3
"""
Check trained Autoencoder model and recommend optimal threshold.
Run this directly on the Edge VM (192.168.182.30).
"""
import pickle
import numpy as np

WEIGHTS_FILE = "autoencoder_weights.pkl"
WINDOW_SIZE = 10

def forward(x, ew1, eb1, dw1, db1):
    a1 = np.maximum(0, np.dot(x, ew1) + eb1)
    return 1 / (1 + np.exp(-np.clip(np.dot(a1, dw1) + db1, -500, 500)))

def main():
    print("=" * 50)
    print("AUTOENCODER THRESHOLD ANALYSIS")
    print("=" * 50)

    # Load weights
    try:
        with open(WEIGHTS_FILE, 'rb') as f:
            w = pickle.load(f)
        print(f"✓ Loaded weights from: {WEIGHTS_FILE}")
        print(f"  Keys: {list(w.keys())}")
    except FileNotFoundError:
        print(f"✗ ERROR: {WEIGHTS_FILE} not found. Run train_autoencoder.py first.")
        return

    ew1 = w['encoder_w1']
    eb1 = w['encoder_b1']
    dw1 = w['decoder_w1']
    db1 = w['decoder_b1']

    # Generate synthetic normal ECG (same formula as ecg_simulator.py)
    print("\n[1/3] Generating normal ECG samples...")
    np.random.seed(42)
    t = np.linspace(0, 50, 5000)
    amplitude, frequency = 1.0, 1.2
    X_normal = np.array([
        amplitude * (np.sin(2 * np.pi * frequency * t[i:i+WINDOW_SIZE]) +
                     0.3 * np.sin(4 * np.pi * frequency * t[i:i+WINDOW_SIZE]))
        for i in range(len(t) - WINDOW_SIZE)
    ])
    print(f"  Normal samples generated: {len(X_normal)}")

    # Generate synthetic anomaly ECG
    print("\n[2/3] Generating anomaly ECG samples...")
    anomaly_errors = []
    for _ in range(500):
        amp = np.random.uniform(0.5, 2.5)
        freq = np.random.uniform(0.5, 3.0)
        i = np.random.randint(0, len(t) - WINDOW_SIZE)
        window = amp * (np.sin(2 * np.pi * freq * t[i:i+WINDOW_SIZE]) +
                        0.3 * np.sin(4 * np.pi * freq * t[i:i+WINDOW_SIZE]))
        recon = forward(window.reshape(1, -1), ew1, eb1, dw1, db1)
        anomaly_errors.append(np.mean((window - recon) ** 2))
    anomaly_errors = np.array(anomaly_errors)

    # Compute reconstruction errors for normal data
    print("\n[3/3] Computing reconstruction errors...")
    recon_normal = forward(X_normal, ew1, eb1, dw1, db1)
    normal_errors = np.mean((X_normal - recon_normal) ** 2, axis=1)

    # Statistics
    print("\n" + "=" * 50)
    print("NORMAL DATA — Reconstruction Error Stats")
    print("=" * 50)
    print(f"  Samples : {len(normal_errors)}")
    print(f"  Min     : {np.min(normal_errors):.4f}")
    print(f"  Mean    : {np.mean(normal_errors):.4f}")
    print(f"  Std     : {np.std(normal_errors):.4f}")
    print(f"  90th pct: {np.percentile(normal_errors, 90):.4f}")
    print(f"  95th pct: {np.percentile(normal_errors, 95):.4f}")
    print(f"  99th pct: {np.percentile(normal_errors, 99):.4f}")
    print(f"  Max     : {np.max(normal_errors):.4f}")

    print("\n" + "=" * 50)
    print("ANOMALY DATA — Reconstruction Error Stats")
    print("=" * 50)
    print(f"  Samples : {len(anomaly_errors)}")
    print(f"  Min     : {np.min(anomaly_errors):.4f}")
    print(f"  Mean    : {np.mean(anomaly_errors):.4f}")
    print(f"  5th pct : {np.percentile(anomaly_errors, 5):.4f}")
    print(f"  Max     : {np.max(anomaly_errors):.4f}")

    # Threshold recommendations
    p95 = np.percentile(normal_errors, 95)
    p99 = np.percentile(normal_errors, 99)

    print("\n" + "=" * 50)
    print("THRESHOLD RECOMMENDATIONS")
    print("=" * 50)
    print(f"  Conservative (low FP) : {p99 + 0.05:.4f}  [99th pct + 0.05]")
    print(f"  Balanced              : {p95 + 0.05:.4f}  [95th pct + 0.05]  ← recommended")
    print(f"  Aggressive (high TPR) : {p95:.4f}          [95th pct]")
    print()

    recommended = round(p95 + 0.05, 4)
    print(f"  ✓ Set THRESHOLD = {recommended} in autoencoder_inference.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
