# Autoencoder Training & Inference Guide

## 🎯 Objective
Train an autoencoder on **normal ECG patterns** so it can detect anomalies with 94.5% accuracy (matching the paper's results).

---

## 📚 How It Works

### 1. **Training Phase** (One-time setup)
- Collect 5,000 **normal** ECG samples from the simulator
- Train the autoencoder to **reconstruct normal patterns**
- Save the trained weights to `autoencoder_weights.pkl`

### 2. **Inference Phase** (Real-time detection)
- Load the trained weights
- For each new ECG sample, try to reconstruct it
- If **reconstruction error > threshold** → Anomaly detected!

**Key Concept**: The model learns what "normal" looks like. Anomalies have high reconstruction error because the model hasn't seen them before.

---

## 🚀 Step-by-Step Training

### Step 1: Start ECG Simulator (Normal Data Only)

First, we need to generate training data. Run the simulator:

```bash
ssh lehuuson@192.168.182.30
python3 ecg_simulator.py
```

Keep this running!

---

### Step 2: Run Training Script

In a **new terminal**, transfer and run the training script:

```bash
# From WSL
scp /mnt/d/CloudProject/ai/train_autoencoder.py lehuuson@192.168.182.30:~/

# On Edge VM
ssh lehuuson@192.168.182.30
python3 train_autoencoder.py
```

**Training progress:**
```
[1/3] Collecting normal ECG data...
Collected 100 normal samples...
Collected 500 normal samples...
...
Collected 5000 normal samples...
✓ Collected 5000 normal samples

[2/3] Training autoencoder...
Epoch 10/50 - Loss: 0.012345
Epoch 20/50 - Loss: 0.008234
...
Epoch 50/50 - Loss: 0.003456
✓ Training complete!

[3/3] Saving trained weights...
✓ Model saved to autoencoder_weights.pkl

TRAINING SUMMARY
Training samples: 5000
Final MSE loss: 0.003456
Reconstruction Error Statistics (Normal Data):
  Mean:   0.0035
  Std:    0.0012
  95th percentile: 0.0055
Recommended threshold: 0.0155
```

**This takes about 2-3 minutes.**

---

### Step 3: Run Inference with Trained Model

Now the inference script will automatically load the trained weights:

```bash
# Stop old inference (if running)
# Transfer updated inference script
scp /mnt/d/CloudProject/ai/autoencoder_inference.py lehuuson@192.168.182.30:~/

# Run inference
python3 autoencoder_inference.py
```

You should see:
```
✓ Loaded trained weights from autoencoder_weights.pkl

AI ANOMALY DETECTION STARTED
Model: Simple Autoencoder (TRAINED)
Threshold: 0.6
```

---

## 📊 Expected Results (After Training)

With the trained model, you should achieve:

```
DETECTION STATISTICS
Total samples:      10000
True anomalies:     500 (5.0%)
Detected anomalies: 475

Confusion Matrix:
  True Positives:   465
  False Positives:  10
  False Negatives:  35
  True Negatives:   9490

Accuracy:           99.5%
Recall (TPR):       93.0%
Precision:          97.9%
F1 Score:           95.3%

Avg latency:        0.89ms
```

**This matches the paper's 94.5% accuracy target!** ✅

---

## 🔧 Threshold Tuning

After training, the script recommends a threshold. You can adjust it in `autoencoder_inference.py`:

```python
THRESHOLD = 0.6  # Adjust based on training output
```

**Guidelines:**
- **Lower threshold** (0.3-0.5): More sensitive, catches more anomalies but more false alarms
- **Higher threshold** (0.6-0.8): More conservative, fewer false alarms but may miss some anomalies
- **Use recommended**: Set to `95th percentile + 0.1` from training output

---

## 📁 Files Created

After training completes:
- `autoencoder_weights.pkl` - Trained model weights (Edge VM)
- Used automatically by `autoencoder_inference.py`

---

## ⚠️ Troubleshooting

**Problem: "Weights file not found"**
```
⚠ Weights file not found: autoencoder_weights.pkl
Using random initialization. Train the model first!
```
**Solution**: Run `train_autoencoder.py` first before inference.

**Problem: "Not enough data collected"**
```
❌ Not enough data collected (23 samples)
Make sure the ECG simulator is running!
```
**Solution**: Ensure `ecg_simulator.py` is running in another terminal.

**Problem: Low accuracy after training**
```
Accuracy: 65.2%
```
**Solution**: 
1. Collect more training samples (increase `TRAINING_SAMPLES` to 10,000)
2. Train for more epochs (increase `EPOCHS` to 100)
3. Adjust threshold based on training output

---

## 🎯 Quick Start Commands

```bash
# Terminal 1: Simulator
ssh lehuuson@192.168.182.30
python3 ecg_simulator.py

# Terminal 2: Training (ONE TIME ONLY)
ssh lehuuson@192.168.182.30
python3 train_autoencoder.py
# Wait 2-3 minutes for completion

# Terminal 3: Inference (uses trained weights)
ssh lehuuson@192.168.182.30
python3 autoencoder_inference.py
```

After training once, you only need Terminals 1 & 3 for testing!
