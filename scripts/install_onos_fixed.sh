#!/bin/bash
# Fixed ONOS Installation Script
# Includes download verification and cleanup

echo "========================================="
echo "Installing ONOS SDN Controller (Fixed)"
echo "========================================="

# Install dependencies
echo "→ Installing dependencies..."
sudo apt update
sudo apt install -y openjdk-11-jdk wget curl unzip

# Verify Java installation
echo "→ Verifying Java..."
java -version

# Clean up any corrupted previous downloads
echo "→ Cleaning up previous downloads..."
cd ~
rm -rf onos-2.7.0*
rm -rf apache-karaf-*

# Try downloading from multiple sources
echo "→ Downloading ONOS..."

# Option 1: Direct download with resume capability
wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz

# Verify download completed
if [ ! -f "onos-2.7.0.tar.gz" ]; then
    echo "ERROR: Download failed!"
    exit 1
fi

FILE_SIZE=$(stat -c%s "onos-2.7.0.tar.gz")
echo "Downloaded file size: $FILE_SIZE bytes"

# Must be around 400MB (400000000 bytes)
if [ "$FILE_SIZE" -lt 300000000 ]; then
    echo "ERROR: File too small, download incomplete!"
    rm onos-2.7.0.tar.gz
    exit 1
fi

# Extract with verbose output
echo "→ Extracting ONOS..."
tar -xzvf onos-2.7.0.tar.gz

# Verify extraction
if [ ! -d "onos-2.7.0" ]; then
    echo "ERROR: Extraction failed!"
    exit 1
fi

cd onos-2.7.0

# Configure ONOS for low memory environment
echo "→ Configuring ONOS for 4GB VM..."
export JAVA_OPTS="-Xms512M -Xmx1536M"

# Start ONOS
echo "→ Starting ONOS service..."
./bin/onos-service start

# Wait for ONOS to start
echo "→ Waiting for ONOS to initialize (90 seconds)..."
for i in {1..18}; do
    sleep 5
    if curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null 2>&1; then
        echo "✓ ONOS is responding!"
        break
    fi
    echo "  ... still waiting ($((i*5))s)"
done

# Verify ONOS is running
echo "→ Verifying ONOS..."
if curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null 2>&1; then
    echo "✓ ONOS REST API is responding"
else
    echo "ERROR: ONOS is not responding"
    echo "Checking logs..."
    tail -50 ~/onos-2.7.0/apache-karaf-*/data/log/karaf.log
    exit 1
fi

# Activate required applications
echo "→ Activating OpenFlow and forwarding apps..."
./bin/onos-app localhost activate org.onosproject.openflow
./bin/onos-app localhost activate org.onosproject.fwd
./bin/onos-app localhost activate org.onosproject.proxyarp

# Show active applications
echo ""
echo "→ Active ONOS applications:"
curl -s -u onos:rocks http://localhost:8181/onos/v1/applications | grep -o '"name":"[^"]*","state":"ACTIVE"' | head -10

echo ""
echo "========================================="
echo "✓ ONOS Installation Complete!"
echo "========================================="
echo "ONOS GUI: http://192.168.182.10:8181/onos/ui"
echo "Login: onos / rocks"
echo "REST API: http://192.168.182.10:8181/onos/v1/"
echo ""
echo "Test command:"
echo "curl -u onos:rocks http://localhost:8181/onos/v1/devices"
echo "========================================="
