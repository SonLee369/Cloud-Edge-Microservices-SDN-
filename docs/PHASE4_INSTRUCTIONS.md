# Phase 4: Analytics Layer Setup (VM 2 - Cloud)

## Overview
Install Apache Kafka on the Cloud VM for real-time data streaming and analytics.

## Prerequisites
✅ Phase 3 in progress (Edge VM components working)
✅ SSH access to Cloud VM (192.168.182.20)

## Step 1: Transfer Kafka Installation Script

From your WSL terminal:

```bash
scp /mnt/d/CloudProject/scripts/install_kafka.sh lehuuson@192.168.182.20:~/
```

## Step 2: Install Kafka

SSH into Cloud VM and run:

```bash
ssh lehuuson@192.168.182.20

# Make script executable
chmod +x install_kafka.sh

# Run installation
./install_kafka.sh
```

**This will:**
- Install Java 11
- Download Kafka 3.6.1
- Configure KRaft mode (no Zookeeper)
- Create healthcare topics
- Optimize for 2GB RAM

**Expected output:**
- ✓ Kafka started
- ✓ Topics created: `healthcare-telemetry`, `healthcare-anomalies`

## Step 3: Test Kafka

While on Cloud VM, test Kafka:

```bash
cd ~/kafka_2.13-3.6.1

# Test producer (type messages, Ctrl+C to exit)
bin/kafka-console-producer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092

# In another SSH session, test consumer
ssh lehuuson@192.168.182.20
cd ~/kafka_2.13-3.6.1
bin/kafka-console-consumer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092 --from-beginning
```

## Step 4: Install Kafka Python Client (for Bridge)

On **Edge VM** (192.168.182.30):

```bash
pip3 install kafka-python
```

## Step 5: Set Up MQTT-Kafka Bridge

Transfer and run the bridge on Edge VM:

```bash
# From WSL
scp /mnt/d/CloudProject/integration/mqtt_kafka_bridge.py lehuuson@192.168.182.30:~/

# On Edge VM
ssh lehuuson@192.168.182.30
chmod +x mqtt_kafka_bridge.py
```

## Testing End-to-End Flow

### Terminal 1 (Edge VM): Run ECG Simulator
```bash
ssh lehuuson@192.168.182.30
python3 ecg_simulator.py
```

### Terminal 2 (Edge VM): Run MQTT-Kafka Bridge
```bash
ssh lehuuson@192.168.182.30
python3 mqtt_kafka_bridge.py
```

### Terminal 3 (Cloud VM): Monitor Kafka
```bash
ssh lehuuson@192.168.182.20
cd ~/kafka_2.13-3.6.1
bin/kafka-console-consumer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092
```

You should see ECG data flowing: **Sensor → MQTT → Bridge → Kafka**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Kafka won't start | Check Java: `java -version` (needs 11) |
| Out of memory | Reduce heap: `export KAFKA_HEAP_OPTS="-Xmx384M"` |
| Bridge can't connect | Check firewall: `sudo ufw status` |
| Topics not created | Manually create: See script commands |

## Next Steps

✅ Phase 4 Complete → Proceed to **AI Inference Deployment** (Phase 3 continuation)
