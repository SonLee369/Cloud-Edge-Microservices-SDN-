#!/usr/bin/env python3
"""
Test 3.3 — Security Breach Simulation
Test 3.3a: Unauthorized MQTT access (rogue device)
Test 3.3b: Network intrusion simulation (hping3 SYN flood)
Run on: WSL (Windows host) — attacks Edge VM 192.168.182.30
"""
import json
import time
import subprocess
import socket
import paho.mqtt.client as mqtt
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
EDGE_IP       = "192.168.182.30"
MQTT_PORT     = 1883
HPING3_DURATION = 10   # seconds for SYN flood

results = {
    "3a": {"sent": 0, "blocked": 0, "detection_ms": None, "enforcement_ms": None},
    "3b": {"packets_sent": 0, "detection_ms": None, "enforcement_ms": None},
}

def separator(title):
    print(f"\n{'='*54}")
    print(f"  {title}")
    print(f"{'='*54}")

SSH_OPTS = ["-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5"]

def get_ovs_flows():
    """Get OVS drop rules via SSH."""
    try:
        out = subprocess.check_output(
            ["ssh"] + SSH_OPTS + [
                f"lehuuson@{EDGE_IP}",
                "sudo ovs-ofctl -O OpenFlow13 dump-flows br0"
            ], stderr=subprocess.DEVNULL, timeout=10).decode()
        flows = [l for l in out.splitlines() if "priority" in l]
        drop_rules = [l for l in flows if "actions=drop" in l]
        return len(flows), len(drop_rules), out
    except Exception as e:
        return -1, -1, str(e)

def check_hping3():
    """Check if hping3 is available."""
    try:
        subprocess.run(["hping3", "--version"],
                       capture_output=True, timeout=3)
        return True
    except FileNotFoundError:
        return False

# ══════════════════════════════════════════════════════════
# TEST 3.3a — Unauthorized MQTT Access
# ══════════════════════════════════════════════════════════
def run_test_3a():
    separator("TEST 3.3a — Unauthorized MQTT Access (Rogue Device)")
    print(f"  Target   : {EDGE_IP}:{MQTT_PORT}")
    print(f"  Started  : {datetime.utcnow().isoformat()}\n")

    # Baseline OVS
    total_before, drops_before, _ = get_ovs_flows()
    print(f"  OVS flows before : {total_before} (drop rules: {drops_before})")

    # Attack 1: Unknown user credentials
    separator("Attack 1 — Invalid credentials (unknown_user)")
    t0 = time.time()
    blocked_count = 0
    sent_count = 0

    for attempt in range(5):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                             client_id=f"ROGUE-{attempt:03d}")
        client.username_pw_set("unknown_user", "invalid_pass")
        connect_result = {"code": None}

        def on_connect(c, userdata, flags, rc, props=None):
            connect_result["code"] = rc

        client.on_connect = on_connect
        try:
            client.connect(EDGE_IP, MQTT_PORT, 5)
            client.loop_start()
            time.sleep(0.5)

            if connect_result["code"] == 0:
                # Connected — try publishing to restricted topic
                payload = json.dumps({
                    "sensor_id" : "ROGUE-001",
                    "value"     : 9.9,
                    "anomaly_injected": True,
                    "attempt"   : attempt,
                })
                info = client.publish("healthcare/admin/config", payload)
                sent_count += 1
                print(f"  [Attempt {attempt+1}] Connected & published to admin topic")
            else:
                blocked_count += 1
                print(f"  [Attempt {attempt+1}] ✅ Blocked — MQTT rc={connect_result['code']}")

            client.loop_stop()
            client.disconnect()
        except Exception as e:
            blocked_count += 1
            print(f"  [Attempt {attempt+1}] ✅ Blocked — {type(e).__name__}: {e}")

    t_auth_done = (time.time() - t0) * 1000

    # Attack 2: Unauthorized topic (no auth required — probe restricted topics)
    separator("Attack 2 — Rogue topic probe (healthcare/admin/config)")
    t1 = time.time()
    client2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                          client_id="ROGUE-PROBE-001")
    try:
        client2.connect(EDGE_IP, MQTT_PORT, 5)
        client2.loop_start()
        time.sleep(0.3)
        for i in range(3):
            payload = json.dumps({
                "cmd"     : "override",
                "priority": "critical",
                "seq"     : i,
            })
            client2.publish("healthcare/admin/config", payload, qos=1)
            sent_count += 1
            time.sleep(0.1)
        client2.loop_stop()
        client2.disconnect()
        print(f"  Rogue probe: 3 messages sent to healthcare/admin/config")
    except Exception as e:
        print(f"  Connection blocked: {e}")

    t_probe_done = (time.time() - t1) * 1000

    # Wait for SDN reaction
    print(f"\n  Waiting 5s for SDN Enforcement Agent to react...")
    time.sleep(5)

    # Check OVS after attack
    total_after, drops_after, flow_dump = get_ovs_flows()
    new_drops = drops_after - drops_before

    results["3a"]["sent"]   = sent_count
    results["3a"]["blocked"] = blocked_count

    separator("RESULTS — Test 3.3a")
    print(f"  Rogue connection attempts : 5")
    print(f"  Blocked by broker         : {blocked_count}")
    print(f"  Messages sent to broker   : {sent_count}")
    print(f"  OVS drop rules before     : {drops_before}")
    print(f"  OVS drop rules after      : {drops_after}")
    print(f"  New drop rules installed  : {new_drops}")
    if new_drops > 0:
        print(f"  SDN reaction              : ✅ Drop rule installed")
    else:
        print(f"  SDN reaction              : ⚠  No new drop rule (check sdn_enforcement.py)")
    print(f"\n  OVS Flow Table:")
    for line in flow_dump.splitlines():
        if "priority" in line:
            print(f"    {line.strip()}")

# ══════════════════════════════════════════════════════════
# TEST 3.3b — Network Intrusion (hping3 SYN flood)
# ══════════════════════════════════════════════════════════
def run_test_3b():
    separator("TEST 3.3b — Network Intrusion (hping3 SYN Flood)")
    print(f"  Target   : {EDGE_IP}:1883 (MQTT port)")
    print(f"  Duration : {HPING3_DURATION}s")
    print(f"  Started  : {datetime.utcnow().isoformat()}\n")

    if not check_hping3():
        print("  [WARN] hping3 not found. Installing...")
        subprocess.run(["sudo", "apt-get", "install", "-y", "hping3"],
                       capture_output=True)
        if not check_hping3():
            print("  [ERROR] Cannot install hping3. Skip Test 3.3b.")
            return

    # OVS baseline
    total_before, drops_before, _ = get_ovs_flows()
    print(f"  OVS flows before : {total_before} (drop rules: {drops_before})")

    # Launch hping3 SYN flood
    separator("Launching SYN Flood")
    print(f"  sudo hping3 -S --flood -p 1883 {EDGE_IP}")
    print(f"  Running for {HPING3_DURATION} seconds...\n")

    t_start = time.time()
    try:
        proc = subprocess.Popen(
            ["sudo", "hping3", "-S", "--flood", "-p", "1883", EDGE_IP],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Monitor OVS every 2 seconds during flood
        drop_detected_at = None
        for elapsed in range(0, HPING3_DURATION, 2):
            time.sleep(2)
            _, drops_now, _ = get_ovs_flows()
            print(f"  [{elapsed+2:2d}s] OVS drop rules: {drops_now}", end="")
            if drops_now > drops_before and drop_detected_at is None:
                drop_detected_at = elapsed + 2
                print(f"  ← ✅ NEW DROP RULE DETECTED at t={drop_detected_at}s")
            else:
                print()

        # Stop hping3 — must use sudo kill (flood mode ignores SIGTERM)
        subprocess.run(["sudo", "kill", "-9", str(proc.pid)],
                       capture_output=True)
        proc.wait(timeout=5)

        flood_duration = time.time() - t_start
        print(f"\n  ✓ SYN flood stopped after {flood_duration:.1f}s")

    except PermissionError:
        print("  [ERROR] hping3 requires sudo. Run: sudo python3 test_security_breach.py")
        return
    except Exception as e:
        print(f"  [ERROR] hping3 failed: {e}")
        return

    # Final OVS check
    time.sleep(3)
    total_after, drops_after, flow_dump = get_ovs_flows()
    new_drops = drops_after - drops_before

    separator("RESULTS — Test 3.3b")
    print(f"  SYN flood duration        : {HPING3_DURATION}s → {EDGE_IP}:1883")
    print(f"  OVS drop rules before     : {drops_before}")
    print(f"  OVS drop rules after      : {drops_after}")
    print(f"  New drop rules installed  : {new_drops}")
    if drop_detected_at:
        print(f"  Drop rule detected at     : t={drop_detected_at}s into flood")
        print(f"  SDN reaction              : ✅ Intrusion blocked by OVS")
    else:
        print(f"  SDN reaction              : ⚠  No drop rule (hping3 operates at L3/L4,")
        print(f"                              OVS rule may need src IP match in sdn_enforcement)")
    print(f"\n  OVS Flow Table:")
    for line in flow_dump.splitlines():
        if "priority" in line:
            print(f"    {line.strip()}")

    # Check iptables on Edge VM
    separator("iptables INPUT chain (Edge VM)")
    try:
        out = subprocess.check_output(
            ["ssh"] + SSH_OPTS + [
                f"lehuuson@{EDGE_IP}",
                "sudo iptables -L INPUT -n -v --line-numbers | head -20"
            ], stderr=subprocess.DEVNULL, timeout=10).decode()
        print(out)
    except Exception as e:
        print(f"  [ERROR] Cannot read iptables: {e}")

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    separator("PHASE 3 — TEST 3.3: SECURITY BREACH SIMULATION")
    print(f"  Edge VM  : {EDGE_IP}")
    print(f"  Time     : {datetime.utcnow().isoformat()}")

    print("\n  [1/2] Running Test 3.3a — Unauthorized MQTT Access")
    run_test_3a()

    print("\n\n  [2/2] Running Test 3.3b — Network Intrusion (hping3)")
    run_test_3b()

    separator("ALL SECURITY TESTS COMPLETE")
    print("  → Ensure sdn_enforcement.py is running on Edge VM during tests")
    print("  → Check OVS drop rules with:")
    print(f"    ssh lehuuson@{EDGE_IP} 'sudo ovs-ofctl -O OpenFlow13 dump-flows br0'")
    print()

if __name__ == "__main__":
    main()
