#!/bin/bash
# fix_security_prereqs.sh
# Run from WSL to fix SSH host key and enable Mosquitto auth on Edge VM
# Usage: bash /mnt/d/CloudProject/scripts/fix_security_prereqs.sh

EDGE_IP="192.168.182.30"
EDGE_USER="lehuuson"
MQTT_USER="lehuuson"
MQTT_PASS="sdn2026"

echo "=================================================="
echo "  Fix Security Prerequisites for Test 3.3"
echo "=================================================="

# ── Fix 1: SSH host key ────────────────────────────────
echo ""
echo "[1/4] Adding Edge VM to SSH known_hosts..."
sudo mkdir -p /root/.ssh
sudo ssh-keyscan -H "$EDGE_IP" 2>/dev/null | sudo tee -a /root/.ssh/known_hosts > /dev/null
echo "  ✓ Host key added for $EDGE_IP"

# Verify SSH works
echo "[1/4] Verifying SSH connection..."
if sudo ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
     "$EDGE_USER@$EDGE_IP" "echo OK" 2>/dev/null | grep -q OK; then
    echo "  ✓ SSH connection to $EDGE_IP: OK"
else
    echo "  ✗ SSH failed — check password or SSH key setup"
    exit 1
fi

# ── Fix 2: Enable Mosquitto auth ──────────────────────
echo ""
echo "[2/4] Creating Mosquitto password file on Edge VM..."
ssh "$EDGE_USER@$EDGE_IP" "
  echo '$MQTT_PASS' | sudo mosquitto_passwd -b -c /etc/mosquitto/passwd $MQTT_USER
  echo '  ✓ Password file created: /etc/mosquitto/passwd'
"

echo ""
echo "[3/4] Writing Mosquitto auth config on Edge VM..."
ssh "$EDGE_USER@$EDGE_IP" "
  sudo tee /etc/mosquitto/conf.d/auth.conf > /dev/null <<EOF
allow_anonymous false
password_file /etc/mosquitto/passwd
EOF
  echo '  ✓ Auth config written: /etc/mosquitto/conf.d/auth.conf'
"

echo ""
echo "[4/4] Restarting Mosquitto and verifying..."
ssh "$EDGE_USER@$EDGE_IP" "
  sudo systemctl restart mosquitto
  sleep 1
  STATUS=\$(sudo systemctl is-active mosquitto)
  if [ \"\$STATUS\" = 'active' ]; then
    echo '  ✓ Mosquitto restarted: active'
  else
    echo '  ✗ Mosquitto failed to restart — check: sudo systemctl status mosquitto'
    exit 1
  fi

  # Test: anonymous should be BLOCKED
  ANON=\$(mosquitto_pub -h localhost -t test -m ping 2>&1)
  if echo \"\$ANON\" | grep -qi 'not authorised\|connection refused\|error'; then
    echo '  ✓ Anonymous access: BLOCKED (auth working)'
  else
    echo '  ⚠ Anonymous access still allowed — check auth.conf'
  fi

  # Test: valid user should be ALLOWED
  AUTH=\$(mosquitto_pub -h localhost -t test -m ping -u $MQTT_USER -P $MQTT_PASS 2>&1)
  if [ -z \"\$AUTH\" ]; then
    echo '  ✓ Authenticated access: ALLOWED (credentials valid)'
  else
    echo '  ⚠ Auth test result: '\$AUTH
  fi
"

echo ""
echo "=================================================="
echo "  All fixes applied!"
echo "=================================================="
echo ""
echo "  NEXT STEPS:"
echo "  1. Update Edge VM scripts with credentials:"
echo "     ssh $EDGE_USER@$EDGE_IP"
echo "     Edit mqtt_kafka_bridge.py, autoencoder_inference.py,"
echo "     sdn_enforcement.py — add:"
echo "       client.username_pw_set('$MQTT_USER', '$MQTT_PASS')"
echo "     before each client.connect(...)"
echo ""
echo "  2. Start full stack on Edge VM:"
echo "     python3 mqtt_kafka_bridge.py"
echo "     python3 autoencoder_inference.py"
echo "     python3 sdn_enforcement.py"
echo ""
echo "  3. Run security test from WSL:"
echo "     sudo python3 /mnt/d/CloudProject/scripts/test_security_breach.py"
echo "=================================================="
