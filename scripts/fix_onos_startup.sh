#!/bin/bash
# Fix ONOS startup issues on Master VM
# Run this after expanding the disk

echo "========================================="
echo "Fixing ONOS Configuration"
echo "========================================="

# Step 1: Set JAVA_HOME permanently
echo "→ Setting JAVA_HOME..."
if ! grep -q "JAVA_HOME" ~/.bashrc; then
    echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
fi

# Load environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "✓ JAVA_HOME set to: $JAVA_HOME"
java -version

# Step 2: Stop any hanging ONOS processes
echo ""
echo "→ Stopping any existing ONOS processes..."
cd ~/onos-2.5.1
./bin/onos-service stop 2>/dev/null || true
sleep 5

# Kill any zombie processes
pkill -f karaf 2>/dev/null || true
sleep 3

# Step 3: Clean up old logs/temp files
echo "→ Cleaning up old ONOS data..."
rm -rf ~/onos-2.5.1/data/* 2>/dev/null || true
rm -rf ~/onos-2.5.1/apache-karaf-*/data/tmp/* 2>/dev/null || true

# Step 4: Start ONOS
echo ""
echo "→ Starting ONOS (this takes 90 seconds)..."
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
./bin/onos-service start

echo "→ Waiting for ONOS to initialize..."
for i in {1..90}; do
    echo -n "."
    sleep 1
done
echo ""

# Step 5: Verify ONOS is running
echo ""
echo "→ Checking ONOS status..."
sleep 5

if curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null 2>&1; then
    echo ""
    echo "========================================="
    echo "✓ ONOS IS RUNNING SUCCESSFULLY!"
    echo "========================================="
    echo "REST API: http://192.168.182.10:8181/onos/v1/applications"
    echo "CLI Access: ~/onos-2.5.1/bin/onos localhost"
    echo "Credentials: onos / rocks"
    echo "========================================="
    
    # Activate essential apps
    echo ""
    echo "→ Activating OpenFlow and Forwarding apps..."
    ~/onos-2.5.1/bin/onos-app localhost activate org.onosproject.openflow
    ~/onos-2.5.1/bin/onos-app localhost activate org.onosproject.fwd
    
    echo ""
    echo "✓ ONOS setup complete!"
else
    echo ""
    echo "⚠ WARNING: ONOS may still be starting..."
    echo "Wait 30 more seconds and check manually:"
    echo "  curl -u onos:rocks http://localhost:8181/onos/v1/applications"
fi
