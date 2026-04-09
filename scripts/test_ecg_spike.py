#!/usr/bin/env python3
"""
Test 3.2 — ECG Traffic Spike
Flood 1000 MQTT messages, measure OVS flow response and SDN metrics.
Deploy on: Edge VM (192.168.182.30)
"""
import json
import time
import subprocess
import paho.mqtt.client as mqtt
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
MQTT_BROKER   = "localhost"
MQTT_TOPIC    = "healthcare/ecg/patient001"
TOTAL_MSGS    = 1000
SENSOR_ID     = "ECG-001"
PATIENT_ID    = "patient001"

# ── Metrics ────────────────────────────────────────────────
results = {
    "sent"         : 0,
    "failed"       : 0,
    "t_start"      : None,
    "t_end"        : None,
    "flows_before" : 0,
    "flows_after"  : 0,
}

def get_ovs_flow_count():
    """Count current flows on br0 via ovs-ofctl."""
    try:
        out = subprocess.check_output(
            ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "br0"],
            stderr=subprocess.DEVNULL
        ).decode()
        return len([l for l in out.splitlines() if "priority" in l])
    except Exception:
        return -1

def dump_ovs_flows():
    """Print full OVS flow table."""
    try:
        out = subprocess.check_output(
            ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "br0"],
            stderr=subprocess.DEVNULL
        ).decode()
        return out.strip()
    except Exception as e:
        return f"[ERROR] Cannot dump flows: {e}"

def separator(title):
    print(f"\n{'='*54}")
    print(f"  {title}")
    print(f"{'='*54}")

# ── Main ───────────────────────────────────────────────────
def main():
    separator("TEST 3.2 — ECG Traffic Spike")
    print(f"  Target   : {TOTAL_MSGS} messages → {MQTT_BROKER}:{MQTT_TOPIC}")
    print(f"  Started  : {datetime.utcnow().isoformat()}")

    # Step 1: Snapshot OVS before flood
    separator("Step 1 — OVS Baseline (before flood)")
    results["flows_before"] = get_ovs_flow_count()
    print(f"  Flow count before : {results['flows_before']}")
    print(dump_ovs_flows())

    # Step 2: Connect MQTT
    separator("Step 2 — Connecting to MQTT broker")
    client = mqtt.Client()
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()
    print(f"  ✓ Connected to {MQTT_BROKER}:1883")

    # Step 3: Flood messages
    separator(f"Step 3 — Flooding {TOTAL_MSGS} MQTT messages")
    results["t_start"] = time.time()

    for i in range(1, TOTAL_MSGS + 1):
        payload = json.dumps({
            "timestamp"       : datetime.utcnow().isoformat(),
            "sensor_id"       : SENSOR_ID,
            "patient_id"      : PATIENT_ID,
            "value"           : 2.5,
            "anomaly_injected": True,
            "seq"             : i,
        })
        info = client.publish(MQTT_TOPIC, payload, qos=1)
        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            results["sent"] += 1
        else:
            results["failed"] += 1

        if i % 200 == 0:
            elapsed = time.time() - results["t_start"]
            rate = i / elapsed
            print(f"  [{i:4d}/{TOTAL_MSGS}] sent={results['sent']} "
                  f"failed={results['failed']} rate={rate:.1f} msg/s")

    results["t_end"] = time.time()
    client.loop_stop()
    client.disconnect()

    total_time = results["t_end"] - results["t_start"]
    throughput  = results["sent"] / total_time

    print(f"\n  ✓ Flood complete in {total_time:.2f}s")
    print(f"  ✓ Throughput: {throughput:.1f} msg/s")

    # Step 4: Wait for SDN reaction
    separator("Step 4 — Waiting 5s for SDN Enforcement Agent to react")
    for remaining in range(5, 0, -1):
        print(f"  ... {remaining}s", end="\r")
        time.sleep(1)

    # Step 5: Snapshot OVS after flood
    separator("Step 5 — OVS After Flood")
    results["flows_after"] = get_ovs_flow_count()
    print(f"  Flow count after  : {results['flows_after']}")
    print(dump_ovs_flows())

    # Step 6: Summary
    separator("RESULTS — Test 3.2 ECG Traffic Spike")
    new_rules = results["flows_after"] - results["flows_before"]
    print(f"  Messages sent     : {results['sent']}")
    print(f"  Messages failed   : {results['failed']}")
    print(f"  Total time        : {total_time:.2f} s")
    print(f"  Throughput        : {throughput:.1f} msg/s")
    print(f"  OVS flows before  : {results['flows_before']}")
    print(f"  OVS flows after   : {results['flows_after']}")
    print(f"  New rules added   : {new_rules}")
    if new_rules > 0:
        print(f"  SDN reaction      : ✅ DETECTED — {new_rules} new flow rule(s) installed")
    else:
        print(f"  SDN reaction      : ⚠  No new flow rules (check sdn_enforcement.py)")
    print(f"{'='*54}")
    print("  → Copy these numbers to your Phase 3 report")
    print(f"{'='*54}\n")

if __name__ == "__main__":
    main()
