#!/usr/bin/env python3
"""
SDN Enforcement Agent
Subscribes to anomaly alerts via MQTT, calls ONOS REST API to push flow rules to OVS.
Deploy on: Edge VM (192.168.182.30)
"""
import json
import time
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────────
MQTT_BROKER      = "localhost"
MQTT_ALERT_TOPIC = "healthcare/anomalies"

ONOS_URL         = "http://192.168.182.10:8181"
ONOS_USER        = "onos"
ONOS_PASS        = "rocks"
ONOS_DEVICE_ID   = "of:00002aed9d98e243"        # OVS br0 on Edge VM 192.168.182.30

MSE_CRITICAL     = 1.5    # Above this → drop rule (high severity)
MSE_WARNING      = 1.2093 # Above this → log only (matches Phase 1 threshold)

# ── Metrics ───────────────────────────────────────────────────────────────────
stats = {
    "alerts_received"  : 0,
    "rules_pushed"     : 0,
    "api_errors"       : 0,
    "response_times_ms": [],
}

# ── ONOS Helpers ──────────────────────────────────────────────────────────────
def get_onos_device_id():
    """Auto-discover OVS device ID from ONOS if not set."""
    try:
        r = requests.get(
            f"{ONOS_URL}/onos/v1/devices",
            auth=(ONOS_USER, ONOS_PASS),
            timeout=5
        )
        devices = r.json().get("devices", [])
        available = [d["id"] for d in devices if d.get("available")]
        if available:
            return available[0]
    except Exception as e:
        print(f"[WARN] Cannot auto-discover device: {e}")
    return None


def push_drop_rule(device_id, timeout_sec=60):
    """
    Push a high-priority DROP rule to OVS via ONOS REST API.
    Returns (rule_id, response_time_ms) or (None, None) on failure.
    """
    flow = {
        "priority"   : 40000,
        "timeout"    : timeout_sec,
        "isPermanent": False,
        "deviceId"   : device_id,
        "treatment"  : {
            "instructions": [{"type": "NOACTION"}]
        },
        "selector"   : {
            "criteria": []
        }
    }

    t_start = time.time()
    try:
        r = requests.post(
            f"{ONOS_URL}/onos/v1/flows/{device_id}",
            params={"appId": "org.onosproject.rest"},
            auth=(ONOS_USER, ONOS_PASS),
            headers={"Content-Type": "application/json"},
            data=json.dumps(flow),
            timeout=10
        )
        response_ms = (time.time() - t_start) * 1000

        if r.status_code in (200, 201):
            try:
                rule_id = r.json().get("flowId", "flow-pushed")
            except Exception:
                rule_id = "flow-pushed"
            return rule_id, response_ms
        else:
            print(f"[ERROR] ONOS returned HTTP {r.status_code}: {r.text[:200]}")
            return None, None
    except requests.exceptions.Timeout:
        print("[ERROR] ONOS REST API timeout")
        return None, None
    except Exception as e:
        print(f"[ERROR] ONOS REST API call failed: {e}")
        return None, None


def get_flow_count(device_id):
    """Return number of flows currently on the device."""
    try:
        r = requests.get(
            f"{ONOS_URL}/onos/v1/flows/{device_id}",
            auth=(ONOS_USER, ONOS_PASS),
            timeout=5
        )
        return len(r.json().get("flows", []))
    except Exception:
        return -1


# ── MQTT Callbacks ────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Connected to MQTT broker: {MQTT_BROKER}:1883")
        client.subscribe(MQTT_ALERT_TOPIC)
        print(f"✓ Subscribed to: {MQTT_ALERT_TOPIC}")
    else:
        print(f"[ERROR] MQTT connection failed (rc={rc})")


def on_message(client, userdata, msg):
    global stats
    t_alert = datetime.utcnow()
    stats["alerts_received"] += 1

    try:
        alert = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print(f"[WARN] Invalid JSON on {msg.topic}")
        return

    mse       = alert.get("mse", 0)
    threshold = alert.get("threshold", MSE_WARNING)
    ts        = alert.get("timestamp", t_alert.isoformat())

    print(f"\n{'='*54}")
    print(f"⚠  ALERT #{stats['alerts_received']}  |  {ts}")
    print(f"   MSE: {mse:.4f}  |  Threshold: {threshold:.4f}")
    print(f"{'='*54}")

    # Determine severity
    if mse < MSE_WARNING:
        print("   Severity: LOW — below threshold, skipping rule push")
        return

    severity = "CRITICAL" if mse >= MSE_CRITICAL else "WARNING"
    print(f"   Severity: {severity}")

    # Resolve device ID
    device_id = ONOS_DEVICE_ID
    if device_id == "REPLACE_WITH_DEVICE_ID":
        print("   [INFO] Auto-discovering ONOS device ID...")
        device_id = get_onos_device_id()
        if not device_id:
            print("   [ERROR] No ONOS device found. Is OVS connected to ONOS?")
            stats["api_errors"] += 1
            return

    # Push flow rule
    print(f"   → Calling ONOS REST API (device: {device_id})...")
    rule_id, response_ms = push_drop_rule(device_id, timeout_sec=60)

    if rule_id:
        stats["rules_pushed"]      += 1
        stats["response_times_ms"].append(response_ms)

        print(f"   ✓ Flow rule pushed  |  Rule ID: {rule_id}")
        print(f"   ✓ ONOS Response Time: {response_ms:.2f} ms")

        flows_now = get_flow_count(device_id)
        print(f"   ✓ Total flows on OVS now: {flows_now}")
    else:
        stats["api_errors"] += 1
        print("   ✗ Failed to push flow rule — check ONOS logs")

    # Print running stats every 5 alerts
    if stats["alerts_received"] % 5 == 0:
        print_stats()


# ── Stats ─────────────────────────────────────────────────────────────────────
def print_stats():
    rt = stats["response_times_ms"]
    avg_rt = sum(rt) / len(rt) if rt else 0
    max_rt = max(rt)            if rt else 0
    print(f"\n{'─'*54}")
    print(f"SDN ENFORCEMENT STATS")
    print(f"  Alerts received : {stats['alerts_received']}")
    print(f"  Rules pushed    : {stats['rules_pushed']}")
    print(f"  API errors      : {stats['api_errors']}")
    if rt:
        print(f"  Avg response    : {avg_rt:.2f} ms")
        print(f"  Max response    : {max_rt:.2f} ms")
    print(f"{'─'*54}\n")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*54)
    print("SDN ENFORCEMENT AGENT")
    print("="*54)
    print(f"MQTT  : {MQTT_BROKER}:1883  →  {MQTT_ALERT_TOPIC}")
    print(f"ONOS  : {ONOS_URL}")
    print(f"Device: {ONOS_DEVICE_ID}")
    print(f"MSE warning threshold  : {MSE_WARNING}")
    print(f"MSE critical threshold : {MSE_CRITICAL}")
    print("="*54 + "\n")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.username_pw_set("lehuuson", "sdn2026")
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n✓ SDN Enforcement Agent stopped")
        print_stats()
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
