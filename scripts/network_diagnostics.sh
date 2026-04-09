#!/bin/bash
# Network diagnostics script - Run on each VM

echo "========================================="
echo "Network Diagnostics Report"
echo "========================================="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

echo "1. Network Interfaces:"
echo "---"
ip addr show
echo ""

echo "2. Routing Table:"
echo "---"
ip route show
echo ""

echo "3. DNS Configuration:"
echo "---"
cat /etc/resolv.conf
echo ""

echo "4. Default Gateway:"
echo "---"
GATEWAY=$(ip route | grep default | awk '{print $3}')
echo "Gateway IP: $GATEWAY"
if [ -n "$GATEWAY" ]; then
    ping -c 3 $GATEWAY
else
    echo "ERROR: No default gateway found!"
fi
echo ""

echo "5. Test Internet (IP - Google DNS):"
echo "---"
ping -c 3 8.8.8.8
echo ""

echo "6. Test DNS Resolution:"
echo "---"
ping -c 3 google.com
echo ""

echo "7. Test HTTP Connectivity:"
echo "---"
curl -I http://google.com 2>&1 | head -5
echo ""

echo "8. VMware Network Info:"
echo "---"
echo "Looking for VMware interfaces..."
ip addr show | grep -i vmware || echo "No VMware interfaces detected"
echo ""

echo "========================================="
echo "Diagnosis Summary:"
echo "========================================="

# Check results
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✓ IP connectivity: WORKING"
else
    echo "✗ IP connectivity: FAILED"
    echo "  → Check VMware NAT settings"
    echo "  → Check gateway: $GATEWAY"
fi

if ping -c 1 google.com &> /dev/null; then
    echo "✓ DNS resolution: WORKING"
else
    echo "✗ DNS resolution: FAILED"
    echo "  → Fix /etc/resolv.conf"
    echo "  → Add: nameserver 8.8.8.8"
fi

if curl -s http://google.com &> /dev/null; then
    echo "✓ HTTP connectivity: WORKING"
    echo ""
    echo "🎉 Internet is working! You can proceed with Kafka installation."
else
    echo "✗ HTTP connectivity: FAILED"
    echo ""
    echo "⚠ Internet not working. See NETWORK_TROUBLESHOOTING.md for fixes."
fi

echo "========================================="
