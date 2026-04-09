#!/usr/bin/env python3
"""
ECG Sensor Simulator
Generates realistic ECG data and publishes to MQTT broker
"""
import time
import json
import random
import math
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT Configuration
BROKER = "192.168.182.30"  # Edge VM (will run Mosquitto)
PORT = 1883
TOPIC = "healthcare/ecg/patient001"

def generate_ecg_sample(t, inject_anomaly=False):
    """
    Generate ECG waveform using sine waves
    Normal heart rate: 60-100 bpm
    """
    if inject_anomaly:
        # Simulate arrhythmia
        amplitude = random.uniform(0.5, 2.5)
        frequency = random.uniform(0.5, 3.0)
    else:
        # Normal ECG
        amplitude = 1.0
        frequency = 1.2  # ~72 bpm
    
    # P-QRS-T complex simplified
    value = amplitude * (math.sin(2 * math.pi * frequency * t) + 
                        0.3 * math.sin(4 * math.pi * frequency * t))
    
    return value

def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    
    print(f"✓ Connected to MQTT broker at {BROKER}:{PORT}")
    print(f"Publishing to topic: {TOPIC}")
    
    t = 0
    sample_rate = 0.01  # 100 Hz
    
    while True:
        # Inject anomaly 5% of the time
        inject_anomaly = random.random() < 0.05
        
        value = generate_ecg_sample(t, inject_anomaly)
        
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_id": "ECG-001",
            "patient_id": "patient001",
            "value": round(value, 4),
            "anomaly_injected": inject_anomaly
        }
        
        client.publish(TOPIC, json.dumps(payload))
        
        if inject_anomaly:
            print(f"⚠ Anomaly: {value:.4f}")
        else:
            print(f"✓ Normal: {value:.4f}")
        
        t += sample_rate
        time.sleep(sample_rate)

if __name__ == "__main__":
    main()
