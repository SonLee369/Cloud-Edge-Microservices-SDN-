#!/bin/bash
# Install Open vSwitch on VM 3 (Edge Node)
# OVS allows SDN controller to manage network flows

echo "========================================="
echo "Installing Open vSwitch on Edge Node"
echo "========================================="

# Install OVS
echo "→ Installing Open vSwitch..."
sudo apt update
sudo apt install -y openvswitch-switch

# Verify installation
echo "→ Verifying OVS installation..."
sudo ovs-vsctl --version

# Create a bridge for SDN-controlled traffic
echo "→ Creating OVS bridge 'br0'..."
sudo ovs-vsctl add-br br0

# Set ONOS as the controller (Master VM IP)
echo "→ Connecting to ONOS controller at 192.168.182.10..."
sudo ovs-vsctl set-controller br0 tcp:192.168.182.10:6653

# Set OpenFlow version to 1.3
sudo ovs-vsctl set bridge br0 protocols=OpenFlow13

# Add the physical network interface to the bridge (optional)
# Uncomment if you want OVS to manage the primary interface
# INTERFACE=$(ip route | grep default | awk '{print $5}')
# sudo ovs-vsctl add-port br0 $INTERFACE

# Verify bridge configuration
echo ""
echo "→ Bridge configuration:"
sudo ovs-vsctl show

echo ""
echo "========================================="
echo "✓ Open vSwitch Installation Complete!"
echo "========================================="
echo "Bridge: br0"
echo "Controller: tcp:192.168.182.10:6653"
echo ""
echo "Verify on ONOS:"
echo "curl -u onos:rocks http://192.168.182.10:8181/onos/v1/devices"
echo "========================================="
