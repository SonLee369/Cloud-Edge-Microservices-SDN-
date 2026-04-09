#!/bin/bash
# Install Apache Kafka (KRaft mode) on VM 2 (Cloud Node)
# KRaft mode = No Zookeeper needed, saves resources

echo "========================================="
echo "Installing Apache Kafka (KRaft Mode)"
echo "========================================="

# Install Java 11
echo "→ Installing Java 11..."
sudo apt update
sudo apt install -y openjdk-11-jdk wget

# Verify Java
java -version

# Download Kafka
echo "→ Downloading Kafka 3.6.1..."
cd ~
wget https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz

# Extract
echo "→ Extracting Kafka..."
tar -xzf kafka_2.13-3.6.1.tgz
cd kafka_2.13-3.6.1

# Generate cluster UUID for KRaft
echo "→ Generating Kafka cluster UUID..."
KAFKA_CLUSTER_ID=$(bin/kafka-storage.sh random-uuid)
echo "Cluster UUID: $KAFKA_CLUSTER_ID"

# Configure Kafka for low-memory environment
echo "→ Configuring Kafka for 2GB VM..."
cat >> config/kraft/server.properties << EOF

# Custom settings for 2GB VM
num.network.threads=3
num.io.threads=4
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
log.retention.hours=1
log.segment.bytes=536870912
EOF

# Format storage
echo "→ Formatting Kafka storage..."
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties

# Start Kafka
echo "→ Starting Kafka..."
export KAFKA_HEAP_OPTS="-Xmx512M -Xms256M"
bin/kafka-server-start.sh -daemon config/kraft/server.properties

# Wait for Kafka to start
echo "→ Waiting for Kafka to start (30 seconds)..."
sleep 30

# Create topics for healthcare telemetry
echo "→ Creating Kafka topics..."
bin/kafka-topics.sh --create --topic healthcare-telemetry \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

bin/kafka-topics.sh --create --topic healthcare-anomalies \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# List topics
echo ""
echo "→ Created topics:"
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

echo ""
echo "========================================="
echo "✓ Kafka Installation Complete!"
echo "========================================="
echo "Kafka broker: 192.168.182.20:9092"
echo "Topics:"
echo "  - healthcare-telemetry (3 partitions)"
echo "  - healthcare-anomalies (1 partition)"
echo ""
echo "Test commands:"
echo "  Produce: bin/kafka-console-producer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092"
echo "  Consume: bin/kafka-console-consumer.sh --topic healthcare-telemetry --bootstrap-server localhost:9092 --from-beginning"
echo "========================================="
