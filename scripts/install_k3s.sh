#!/bin/bash
# Install K3s on VM 1 (Master Node)
# This script installs a lightweight Kubernetes distribution

echo "========================================="
echo "Installing K3s on Master Node"
echo "========================================="

# Install K3s without traefik (to save resources)
echo "→ Downloading and installing K3s..."
curl -sfL https://get.k3s.io | sh -s - --disable traefik

# Wait for K3s to be ready
echo "→ Waiting for K3s to start..."
sleep 10

# Check K3s status
echo "→ Checking K3s status..."
sudo systemctl status k3s --no-pager

# Get node token (save this for KubeEdge later)
echo ""
echo "========================================="
echo "K3s Node Token (SAVE THIS!):"
echo "========================================="
sudo cat /var/lib/rancher/k3s/server/node-token
echo ""

# Verify installation
echo "→ Verifying K3s installation..."
sudo k3s kubectl get nodes

echo ""
echo "========================================="
echo "K3s Installation Complete!"
echo "========================================="
echo "Next: Install ONOS SDN Controller"
