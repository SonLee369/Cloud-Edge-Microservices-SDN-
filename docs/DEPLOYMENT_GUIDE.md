# Complete System Deployment Guide

## 📋 Current Progress

✅ **Phase 1**: Infrastructure verified
✅ **Phase 2**: K3s + ONOS running on Master
✅ **Phase 3**: MQTT + ECG simulator working on Edge
🔄 **Phase 4**: Ready to install Kafka on Cloud

---

## 🚀 Next Steps: Complete the System

### Step 1: Install Kafka on Cloud VM (10 min)

```bash
# From WSL
scp /mnt/d/CloudProject/scripts/install_kafka.sh lehuuson@192.168.182.20:~/

# On Cloud VM
ssh lehuuson@192.168.192.20
chmod +x install_kafka.sh
./install_kafka.sh
```

### Step 2: Deploy AI Inference on Edge VM (5 min)

```bash
# From WSL
scp /mnt/d/CloudProject/ai/autoencoder_inference.py lehuuson@192.168.182.30:~/

# On Edge VM
ssh lehuuson@192.168.182.30
python3 autoencoder_inference.py
```

This starts **real-time anomaly detection** on the Edge!

### Step 3: Set Up Data Pipeline (5 min)

```bash
# Install Kafka client on Edge
ssh lehuuson@192.168.182.30
pip3 install kafka-python

# Transfer bridge script
# From WSL:
scp /mnt/d/CloudProject/integration/mqtt_kafka_bridge.py lehuuson@192.168.182.30:~/
```

---

## 🧪 Phase 6: Verification Testing

### Test 1: Anomaly Detection Accuracy (Target: 94.5%)

**On Edge VM**, run AI inference alongside ECG simulator:

```bash
# Terminal 1: ECG Simulator
python3 ecg_simulator.py

# Terminal 2: AI Inference
python3 autoencoder_inference.py
```

Let it run for 1000+ samples. The AI will print accuracy stats every 100 samples.

**Expected result**: ~94% accuracy

---

### Test 2: Inference Latency (Target: 35.2 ms)

The `autoencoder_inference.py` automatically measures latency for each inference.

**Expected result**: Average latency ~10-30ms (better than paper's 35.2ms target)

---

### Test 3: Security Test (Target: 72% reduction)

**From WSL**, simulate attack:

```bash
# Install hping3
sudo apt install hping3

# Baseline attack (no SDN protection)
sudo hping3 -S --flood -p 80 192.168.182.30
```

Watch the packet rate. Then **configure ONOS** to block:

```bash
# On Master VM
ssh lehuuson@192.168.182.10

# Install flow rule to drop SYN flood
cd ~/onos-2.5.1
./bin/onos-app localhost activate org.onosproject.fwd

# Use ONOS CLI to add ACL (or use REST API)
```

Re-run attack and compare packet counts.

**Expected result**: 70%+ reduction in successful packets

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│             MASTER VM (192.168.182.10)          │
│  ┌──────────┐              ┌──────────┐         │
│  │   K3s    │              │  ONOS    │         │
│  │ Control  │              │   SDN    │         │
│  │  Plane   │              │Controller│         │
│  └──────────┘              └────┬─────┘         │
└──────────────────────────────────┼──────────────┘
                                   │ OpenFlow
                                   ▼
┌─────────────────────────────────────────────────┐
│              EDGE VM (192.168.182.30)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   OVS    │  │  MQTT    │  │    AI    │      │
│  │  Bridge  │  │  Broker  │  │Inference │      │
│  └──────────┘  └────┬─────┘  └────┬─────┘      │
│                     │              │            │
│  ┌──────────────────▼──────────────▼─────┐     │
│  │        ECG Simulator (Python)         │     │
│  └───────────────────────────────────────┘     │
└─────────────────┬───────────────────────────────┘
                  │ Kafka
                  ▼
┌─────────────────────────────────────────────────┐
│             CLOUD VM (192.168.182.20)           │
│  ┌──────────────────────────────────────┐       │
│  │         Apache Kafka (KRaft)         │       │
│  │  Topics: healthcare-telemetry        │       │
│  │         healthcare-anomalies         │       │
│  └──────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Summary of Components

| VM | Component | Purpose | Status |
|----|-----------|---------|--------|
| Master | K3s | Kubernetes control plane | ✅ Running |
| Master | ONOS 2.5.1 | SDN controller | ✅ Running |
| Edge | Open vSwitch | SDN data plane | ⚠️ Pending |
| Edge | Mosquitto | MQTT broker | ✅ Running |
| Edge | ECG Simulator | Sensor data generation | ✅ Tested |
| Edge | AI Inference | Anomaly detection | 📦 Ready |
| Cloud | Kafka | Analytics streaming | 📦 Ready |

---

## 📝 Quick Reference Commands

### Start Full System

```bash
# Master VM
ssh lehuuson@192.168.182.10
cd ~/onos-2.5.1 && ./bin/onos-service status

# Edge VM - Terminal 1
ssh lehuuson@192.168.182.30
python3 ecg_simulator.py

# Edge VM - Terminal 2
python3 autoencoder_inference.py

# Cloud VM
ssh lehuuson@192.168.182.20
cd ~/kafka_2.13-3.6.1 && bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Monitor System

```bash
# View anomaly detections
ssh lehuuson@192.168.182.30
mosquitto_sub -h localhost -t 'healthcare/anomalies'

# View Kafka stream
ssh lehuuson@192.168.182.20
cd ~/kafka_2.13-3.6.1
bin/kafka-console-consumer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092
```
