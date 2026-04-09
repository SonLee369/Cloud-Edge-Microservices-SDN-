#!/bin/bash
# Install Python dependencies for sensor simulation on Edge VM

echo "========================================="
echo "Installing Python Dependencies"
echo "========================================="

# Install Python and pip
echo "→ Installing Python3 and pip..."
sudo apt update
sudo apt install -y python3 python3-pip

# Install MQTT client library
echo "→ Installing paho-mqtt..."
pip3 install paho-mqtt

# Install other useful libraries
echo "→ Installing additional libraries..."
pip3 install numpy

# Verify installations
echo ""
echo "→ Verifying installations..."
python3 --version
pip3 --version
python3 -c "import paho.mqtt.client as mqtt; print('✓ paho-mqtt installed')"
python3 -c "import numpy; print('✓ numpy installed')"

echo ""
echo "========================================="
echo "✓ Python Dependencies Installed!"
echo "========================================="
echo "Ready to run sensor simulators"
echo "========================================="
