#!/bin/bash
# Install ONOS 2.5.1 (smaller, more stable)

echo "========================================="
echo "Installing ONOS 2.5.1 (Alternative)"
echo "========================================="

# Clean up
cd ~
rm -rf onos-2.*

# Download smaller ONOS version
echo "→ Downloading ONOS 2.5.1..."
wget --tries=3 --continue https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.5.1/onos-2.5.1.tar.gz

# Check file size
FILE_SIZE=$(stat -c%s "onos-2.5.1.tar.gz" 2>/dev/null || echo "0")
echo "File size: $FILE_SIZE bytes"

if [ "$FILE_SIZE" -lt 100000000 ]; then
    echo "ERROR: Download too small, retrying..."
    rm onos-2.5.1.tar.gz
    wget https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.5.1/onos-2.5.1.tar.gz
fi

# Extract
echo "→ Extracting..."
tar -xzf onos-2.5.1.tar.gz
cd onos-2.5.1

# Start ONOS
echo "→ Starting ONOS..."
export JAVA_OPTS="-Xms512M -Xmx1536M"
./bin/onos-service start

# Wait and test
echo "→ Waiting 90 seconds..."
sleep 90

# Test
curl -u onos:rocks http://localhost:8181/onos/v1/applications

# Activate apps
echo "→ Activating OpenFlow..."
./bin/onos-app localhost activate org.onosproject.openflow
./bin/onos-app localhost activate org.onosproject.fwd

echo ""
echo "✓ ONOS 2.5.1 Installation Complete!"
echo "Test: curl -u onos:rocks http://localhost:8181/onos/v1/devices"
