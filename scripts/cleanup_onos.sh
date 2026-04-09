#!/bin/bash
# Clean up ONOS zombie processes and corrupted cache

echo "========================================="
echo "Cleaning Up ONOS"
echo "========================================="

# Step 1: Kill all ONOS/Karaf processes
echo "→ Killing all ONOS/Karaf processes..."
pkill -9 -f karaf
pkill -9 -f onos
sleep 3

# Step 2: Kill anything using port 8181
echo "→ Freeing port 8181..."
sudo fuser -k 8181/tcp 2>/dev/null || true
sleep 2

# Step 3: Remove ALL ONOS data and cache
echo "→ Removing corrupted cache and data..."
cd ~
rm -rf onos-2.5.1/apache-karaf-*/data/*
rm -rf onos-2.5.1/data/*
rm -rf .m2/repository/org/onosproject/* 2>/dev/null || true

# Step 4: Verify port is free
echo "→ Verifying port 8181 is free..."
if sudo lsof -i :8181 > /dev/null 2>&1; then
    echo "ERROR: Port 8181 still in use!"
    sudo lsof -i :8181
    exit 1
else
    echo "✓ Port 8181 is free"
fi

echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo "Now manually start ONOS:"
echo "  cd ~/onos-2.5.1"
echo "  export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
echo "  ./bin/onos-service start"
echo "========================================="
