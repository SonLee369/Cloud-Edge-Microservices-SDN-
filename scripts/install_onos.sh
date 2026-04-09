#!/bin/bash
# Install ONOS SDN Controller on VM 1 (Master Node)
# ONOS provides REST APIs for network programmability

echo "========================================="
echo "Installing ONOS SDN Controller"
echo "========================================="

# Install Java (ONOS dependency)
echo "→ Installing Java 11..."
sudo apt update
sudo apt install -y openjdk-11-jdk wget

# Verify Java installation
java -version

# Download ONOS
echo "→ Downloading ONOS 2.7.0..."
cd ~
wget https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz

echo "→ Extracting ONOS..."
tar xzf onos-2.7.0.tar.gz
cd onos-2.7.0

# Start ONOS
echo "→ Starting ONOS service..."
./bin/onos-service start

# Wait for ONOS to start (takes ~60 seconds)
echo "→ Waiting for ONOS to initialize (60 seconds)..."
sleep 60

# Verify ONOS is running
echo "→ Verifying ONOS is running..."
curl -u onos:rocks http://localhost:8181/onos/v1/applications

echo ""
echo "→ Activating OpenFlow application..."
./bin/onos-app localhost activate org.onosproject.openflow
./bin/onos-app localhost activate org.onosproject.fwd

echo ""
echo "========================================="
echo "ONOS Installation Complete!"
echo "========================================="
echo "ONOS GUI: http://192.168.182.10:8181/onos/ui"
echo "Login: onos / rocks"
echo "REST API: http://192.168.182.10:8181/onos/v1/"
echo "========================================="
