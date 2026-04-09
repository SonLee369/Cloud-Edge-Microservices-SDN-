#!/bin/bash
# Run ONOS in Docker container

echo "========================================="
echo "Starting ONOS in Docker"
echo "========================================="

# Clean up old corrupted ONOS installation
echo "→ Cleaning up old ONOS installation..."
sudo pkill -9 -f karaf 2>/dev/null || true
sudo fuser -k 8181/tcp 2>/dev/null || true
rm -rf ~/onos-2.5.1 2>/dev/null || true

# Stop and remove any existing ONOS container
echo "→ Removing any existing ONOS container..."
sudo docker stop onos 2>/dev/null || true
sudo docker rm onos 2>/dev/null || true

# Pull ONOS Docker image
echo "→ Pulling ONOS Docker image (this may take a few minutes)..."
sudo docker pull onosproject/onos:2.5.1

# Run ONOS container
echo "→ Starting ONOS container..."
sudo docker run -d \
  --name onos \
  --restart unless-stopped \
  -p 8181:8181 \
  -p 8101:8101 \
  -p 6653:6653 \
  onosproject/onos:2.5.1

echo ""
echo "→ Waiting for ONOS to start (60 seconds)..."
for i in {1..60}; do
    echo -n "."
    sleep 1
done
echo ""

# Wait for ONOS REST API to be ready
echo "→ Waiting for ONOS REST API..."
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null 2>&1; then
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

# Verify ONOS is running
echo ""
if curl -s -u onos:rocks http://localhost:8181/onos/v1/applications > /dev/null 2>&1; then
    echo "========================================="
    echo "✓ ONOS IS RUNNING IN DOCKER!"
    echo "========================================="
    echo "Container: onos"
    echo "REST API: http://192.168.182.10:8181/onos/v1/applications"
    echo "OpenFlow: port 6653"
    echo "Credentials: onos / rocks"
    echo ""
    echo "Useful commands:"
    echo "  sudo docker logs onos              # View logs"
    echo "  sudo docker exec -it onos bash     # Enter container"
    echo "  sudo docker stop onos              # Stop ONOS"
    echo "  sudo docker start onos             # Start ONOS"
    echo "  sudo docker restart onos           # Restart ONOS"
    echo "========================================="
    
    # Activate essential apps
    echo ""
    echo "→ Activating OpenFlow apps..."
    sudo docker exec onos /root/onos/bin/onos-app localhost activate org.onosproject.openflow
    sudo docker exec onos /root/onos/bin/onos-app localhost activate org.onosproject.fwd
    
    echo ""
    echo "✓ ONOS setup complete!"
else
    echo "========================================="
    echo "⚠ ONOS may still be initializing..."
    echo "========================================="
    echo "Check status with:"
    echo "  sudo docker logs onos"
    echo "  curl -u onos:rocks http://localhost:8181/onos/v1/applications"
fi
