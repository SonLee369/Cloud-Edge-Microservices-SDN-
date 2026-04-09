#!/bin/bash
# Install Mosquitto MQTT Broker on VM 3 (Edge Node)

echo "========================================="
echo "Installing Mosquitto MQTT Broker"
echo "========================================="

# Install Mosquitto
echo "→ Installing Mosquitto..."
sudo apt update
sudo apt install -y mosquitto mosquitto-clients

# Enable and start Mosquitto
echo "→ Starting Mosquitto service..."
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Configure to allow anonymous connections (for testing)
echo "→ Configuring Mosquitto..."
sudo bash -c 'cat > /etc/mosquitto/conf.d/custom.conf << EOF
listener 1883
allow_anonymous true
EOF'

# Restart to apply config
sudo systemctl restart mosquitto

# Verify Mosquitto is running
echo "→ Verifying Mosquitto status..."
sudo systemctl status mosquitto --no-pager

# Test MQTT
echo ""
echo "→ Testing MQTT (publishing test message)..."
mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"
echo "✓ MQTT test message sent"

echo ""
echo "========================================="
echo "✓ Mosquitto MQTT Broker Installed!"
echo "========================================="
echo "Broker: 192.168.182.30:1883"
echo "Anonymous access: Enabled (for testing)"
echo ""
echo "Test commands:"
echo "  Subscribe: mosquitto_sub -h localhost -t 'healthcare/#'"
echo "  Publish:   mosquitto_pub -h localhost -t 'healthcare/test' -m 'test'"
echo "========================================="
