#!/usr/bin/env python3
"""
MQTT to Kafka Bridge
Subscribes to MQTT topics on Edge and forwards to Kafka on Cloud
"""
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import json
import sys

# Configuration
MQTT_BROKER = "localhost"  # Run on Edge VM
MQTT_TOPIC = "healthcare/#"
KAFKA_BROKER = "192.168.182.20:9092"  # Cloud VM
KAFKA_TOPIC = "healthcare-telemetry"

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=3,
        max_in_flight_requests_per_connection=1
    )
    print(f"✓ Connected to Kafka broker: {KAFKA_BROKER}")
except Exception as e:
    print(f"ERROR: Cannot connect to Kafka: {e}")
    sys.exit(1)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Connected to MQTT broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"✓ Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"ERROR: MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        # Parse MQTT message
        payload = json.loads(msg.payload.decode())
        
        # Add metadata
        payload['mqtt_topic'] = msg.topic
        
        # Forward to Kafka
        future = producer.send(KAFKA_TOPIC, payload)
        future.get(timeout=10)  # Block until sent
        
        print(f"→ Forwarded: {msg.topic} | Value: {payload.get('value', 'N/A')}")
        
    except json.JSONDecodeError:
        print(f"WARNING: Invalid JSON from {msg.topic}")
    except Exception as e:
        print(f"ERROR: Failed to forward message: {e}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    print("\n========================================")
    print("MQTT → Kafka Bridge Started")
    print("========================================")
    print(f"MQTT:  {MQTT_BROKER}:1883 ({MQTT_TOPIC})")
    print(f"Kafka: {KAFKA_BROKER} ({KAFKA_TOPIC})")
    print("========================================\n")
    
    client.loop_forever()
    
except KeyboardInterrupt:
    print("\n✓ Bridge stopped by user")
    producer.close()
    client.disconnect()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
