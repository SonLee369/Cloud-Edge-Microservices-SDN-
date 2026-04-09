#!/bin/bash
# Quick deployment script - Run this on Edge VM to set up AI inference

echo "========================================="
echo "Final Edge VM Setup"
echo "========================================="

# Install Kafka Python client
echo "→ Installing Kafka Python client..."
pip3 install kafka-python

echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Files ready:"
echo "  - ecg_simulator.py (sensor data)"
echo "  - autoencoder_inference.py (AI detection)"
echo "  - mqtt_kafka_bridge.py (optional - cloud integration)"
echo ""
echo "========================================="
echo "🚀 START TESTING"
echo "========================================="
echo ""
echo "Terminal 1: Start ECG Simulator"
echo "  python3 ecg_simulator.py"
echo ""
echo "Terminal 2: Start AI Inference"
echo "  python3 autoencoder_inference.py"
echo ""
echo "Let it run for 5-10 minutes to collect statistics."
echo "The AI will automatically print accuracy and latency every 100 samples."
echo ""
echo "========================================="
