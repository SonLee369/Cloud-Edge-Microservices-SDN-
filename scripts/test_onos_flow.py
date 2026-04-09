#!/usr/bin/env python3
"""
ONOS Flow Rule Format Tester
Run on Master VM (192.168.182.10) to find the correct API format.
"""
import json
import requests

ONOS_URL  = "http://localhost:8181"
ONOS_USER = "onos"
ONOS_PASS = "rocks"
DEVICE_ID = "of:00002aed9d98e243"

def separator(title):
    print(f"\n{'='*54}")
    print(f"  {title}")
    print(f"{'='*54}")

# ── Test C: ONOS version ───────────────────────────────────
separator("Test C — ONOS Version Info")
try:
    r = requests.get(f"{ONOS_URL}/onos/v1/info",
                     auth=(ONOS_USER, ONOS_PASS), timeout=5)
    print(f"HTTP {r.status_code}")
    info = r.json()
    print(f"  Version : {info.get('version', 'N/A')}")
    print(f"  Commit  : {info.get('commit',  'N/A')}")
    print(f"  Built   : {info.get('buildTime','N/A')}")
except Exception as e:
    print(f"ERROR: {e}")

# ── Test A: Single flow body ───────────────────────────────
separator("Test A — Single flow (no 'flows' wrapper)")
body_a = {
    "priority"   : 40000,
    "timeout"    : 60,
    "isPermanent": False,
    "deviceId"   : DEVICE_ID,
    "treatment"  : {"instructions": [{"type": "NOACTION"}]},
    "selector"   : {"criteria": []}
}
try:
    r = requests.post(
        f"{ONOS_URL}/onos/v1/flows/{DEVICE_ID}",
        params={"appId": "org.onosproject.rest"},
        auth=(ONOS_USER, ONOS_PASS),
        headers={"Content-Type": "application/json"},
        data=json.dumps(body_a),
        timeout=10
    )
    print(f"HTTP {r.status_code}")
    print(f"Response: {r.text[:300]}")
    if r.status_code in (200, 201):
        print("  >>> TEST A PASSED <<<")
except Exception as e:
    print(f"ERROR: {e}")

# ── Test B: Batch with flows array ─────────────────────────
separator("Test B — Batch (wrapped in 'flows' array)")
body_b = {
    "flows": [{
        "priority"   : 40000,
        "timeout"    : 60,
        "isPermanent": False,
        "deviceId"   : DEVICE_ID,
        "treatment"  : {"instructions": [{"type": "NOACTION"}]},
        "selector"   : {"criteria": []}
    }]
}
try:
    r = requests.post(
        f"{ONOS_URL}/onos/v1/flows/{DEVICE_ID}",
        params={"appId": "org.onosproject.rest"},
        auth=(ONOS_USER, ONOS_PASS),
        headers={"Content-Type": "application/json"},
        data=json.dumps(body_b),
        timeout=10
    )
    print(f"HTTP {r.status_code}")
    print(f"Response: {r.text[:300]}")
    if r.status_code in (200, 201):
        print("  >>> TEST B PASSED <<<")
except Exception as e:
    print(f"ERROR: {e}")

# ── Summary ────────────────────────────────────────────────
separator("Done — paste full output to Claude")
