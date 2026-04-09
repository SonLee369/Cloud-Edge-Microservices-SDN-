#!/bin/bash
# Set up Kafka with Docker Compose on Cloud VM

echo "========================================="
echo "Setting Up Kafka with Docker Compose"
echo "========================================="

# Step 1: Install Docker (if not already installed)
if ! command -v docker &> /dev/null; then
    echo "→ Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    sudo usermod -aG docker $USER
    sudo systemctl start docker
    sudo systemctl enable docker
    
    echo "✓ Docker installed"
else
    echo "✓ Docker already installed"
fi

# Step 2: Start Kafka with Docker Compose
echo ""
echo "→ Starting Kafka container..."
sudo docker compose -f ~/docker-compose-kafka.yml up -d

# Step 3: Wait for Kafka to be ready
echo ""
echo "→ Waiting for Kafka to start (60 seconds)..."
sleep 60

# Step 4: Create topics
echo ""
echo "→ Creating healthcare topics..."
sudo docker exec kafka kafka-topics.sh --create \
  --topic healthcare-telemetry \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

sudo docker exec kafka kafka-topics.sh --create \
  --topic healthcare-anomalies \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

# Step 5: Verify
echo ""
echo "→ Verifying topics..."
sudo docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

echo ""
echo "========================================="
echo "✓ Kafka Setup Complete!"
echo "========================================="
echo "Kafka broker: 192.168.182.20:9092"
echo ""
echo "Useful commands:"
echo "  sudo docker compose -f ~/docker-compose-kafka.yml logs -f    # View logs"
echo "  sudo docker compose -f ~/docker-compose-kafka.yml stop       # Stop Kafka"
echo "  sudo docker compose -f ~/docker-compose-kafka.yml start      # Start Kafka"
echo "  sudo docker compose -f ~/docker-compose-kafka.yml down       # Remove Kafka"
echo "  sudo docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092"
echo "========================================="
