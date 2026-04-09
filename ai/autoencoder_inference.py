#!/usr/bin/env python3
"""
Autoencoder-based Anomaly Detection for Healthcare IoT
Monitors ECG data and detects anomalies in real-time
"""
import numpy as np
import time
import json
import paho.mqtt.client as mqtt
from collections import deque
from datetime import datetime

# Configuration
MQTT_BROKER = "localhost"  # Edge VM
MQTT_INPUT_TOPIC = "healthcare/ecg/#"
MQTT_OUTPUT_TOPIC = "healthcare/anomalies"
WINDOW_SIZE = 10  # Number of samples for inference
THRESHOLD = 0.5  # MSE threshold - tuned for balance between precision and recall

# Simple Autoencoder (using numpy for lightweight deployment)
class SimpleAutoencoder:
    """Lightweight autoencoder for edge deployment"""
    
    def __init__(self, input_dim=10, weights_file=None):
        self.input_dim = input_dim
        
        if weights_file:
            # Load pre-trained weights
            try:
                import pickle
                with open(weights_file, 'rb') as f:
                    weights = pickle.load(f)
                self.encoder_w1 = weights['encoder_w1']
                self.encoder_b1 = weights['encoder_b1']
                self.decoder_w1 = weights['decoder_w1']
                self.decoder_b1 = weights['decoder_b1']
                print(f"✓ Loaded trained weights from {weights_file}")
            except FileNotFoundError:
                print(f"⚠ Weights file not found: {weights_file}")
                print("  Using random initialization. Train the model first!")
                self._init_random_weights()
        else:
            # Random initialization (fallback)
            self._init_random_weights()
    
    def _init_random_weights(self):
        """Initialize with random weights"""
        np.random.seed(42)
        self.encoder_w1 = np.random.randn(self.input_dim, 6) * 0.3
        self.encoder_b1 = np.zeros(6)
        self.decoder_w1 = np.random.randn(6, self.input_dim) * 0.3
        self.decoder_b1 = np.zeros(self.input_dim)
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, x):
        """Forward pass through autoencoder"""
        # Encoder
        encoded = self.relu(np.dot(x, self.encoder_w1) + self.encoder_b1)
        # Decoder
        decoded = self.sigmoid(np.dot(encoded, self.decoder_w1) + self.decoder_b1)
        return decoded
    
    def predict(self, x):
        """Predict and calculate reconstruction error"""
        reconstruction = self.forward(x)
        mse = np.mean((x - reconstruction) ** 2)
        return mse, reconstruction

# Global variables
WEIGHTS_FILE = "autoencoder_weights.pkl"  # Trained model weights
model = SimpleAutoencoder(WINDOW_SIZE, weights_file=WEIGHTS_FILE)
data_buffer = deque(maxlen=WINDOW_SIZE)
stats = {
    'total_samples': 0,
    'anomalies_detected': 0,
    'true_anomalies': 0,
    'true_positives': 0,   # Correctly detected anomalies
    'false_positives': 0,  # Normal data flagged as anomaly
    'false_negatives': 0,  # Missed anomalies
    'latencies': []
}

def on_message(client, userdata, msg):
    """Process incoming ECG data"""
    global stats
    
    start_time = time.time()
    
    try:
        # Parse message
        data = json.loads(msg.payload.decode())
        value = data.get('value', 0)
        ground_truth = data.get('anomaly_injected', False)
        
        # Add to buffer
        data_buffer.append(value)
        stats['total_samples'] += 1
        
        if ground_truth:
            stats['true_anomalies'] += 1
        
        # Wait until buffer is full
        if len(data_buffer) < WINDOW_SIZE:
            return
        
        # Prepare input
        sample = np.array(list(data_buffer)).reshape(1, -1)
        
        # Inference
        mse, reconstruction = model.predict(sample)
        
        # Anomaly detection
        is_anomaly = mse > THRESHOLD
        
        # Update confusion matrix
        if is_anomaly and ground_truth:
            stats['true_positives'] += 1  # Correctly detected anomaly
        elif is_anomaly and not ground_truth:
            stats['false_positives'] += 1  # False alarm
        elif not is_anomaly and ground_truth:
            stats['false_negatives'] += 1  # Missed anomaly
        # else: True negative (correctly identified normal)
        
        if is_anomaly:
            stats['anomalies_detected'] += 1
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        stats['latencies'].append(latency_ms)
        
        # Keep only last 1000 latencies
        if len(stats['latencies']) > 1000:
            stats['latencies'] = stats['latencies'][-1000:]
        
        # Log result
        status = "⚠ ANOMALY" if is_anomaly else "✓ Normal"
        print(f"{status} | MSE: {mse:.4f} | Latency: {latency_ms:.2f}ms | GT: {ground_truth}")
        
        # Publish anomaly alert
        if is_anomaly:
            alert = {
                'timestamp': datetime.utcnow().isoformat(),
                'mse': float(mse),
                'threshold': THRESHOLD,
                'values': list(data_buffer),
                'ground_truth': ground_truth,
                'latency_ms': latency_ms
            }
            client.publish(MQTT_OUTPUT_TOPIC, json.dumps(alert))
        
        # Print stats every 100 samples
        if stats['total_samples'] % 100 == 0:
            print_stats()
    
    except Exception as e:
        print(f"ERROR: {e}")

def print_stats():
    """Print detection statistics"""
    total = stats['total_samples']
    detected = stats['anomalies_detected']
    true_anom = stats['true_anomalies']
    tp = stats['true_positives']
    fp = stats['false_positives']
    fn = stats['false_negatives']
    tn = total - (tp + fp + fn)  # True negatives
    
    avg_latency = np.mean(stats['latencies']) if stats['latencies'] else 0
    max_latency = max(stats['latencies']) if stats['latencies'] else 0
    
    # Calculate metrics (with zero checks)
    recall = (tp / true_anom * 100) if true_anom > 0 else 0
    precision = (tp / detected * 100) if detected > 0 else 0
    accuracy = ((tp + tn) / total * 100) if total > 0 else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    anomaly_rate = (true_anom / total * 100) if total > 0 else 0
    
    print("\n" + "="*50)
    print("DETECTION STATISTICS")
    print("="*50)
    print(f"Total samples:      {total}")
    print(f"True anomalies:     {true_anom} ({anomaly_rate:.1f}%)")
    print(f"Detected anomalies: {detected}")
    print("")
    print("Confusion Matrix:")
    print(f"  True Positives:   {tp}")
    print(f"  False Positives:  {fp}")
    print(f"  False Negatives:  {fn}")
    print(f"  True Negatives:   {tn}")
    print("")
    print(f"Accuracy:           {accuracy:.1f}%")
    print(f"Recall (TPR):       {recall:.1f}%")
    print(f"Precision:          {precision:.1f}%")
    print(f"F1 Score:           {f1_score:.1f}%")
    print("")
    print(f"Avg latency:        {avg_latency:.2f}ms")
    print(f"Max latency:        {max_latency:.2f}ms")
    print("="*50 + "\n")

def main():
    client = mqtt.Client()
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        client.subscribe(MQTT_INPUT_TOPIC)
        
        print("\n" + "="*50)
        print("AI ANOMALY DETECTION STARTED")
        print("="*50)
        print(f"Model: Simple Autoencoder")
        print(f"Input:  {MQTT_INPUT_TOPIC}")
        print(f"Output: {MQTT_OUTPUT_TOPIC}")
        print(f"Window: {WINDOW_SIZE} samples")
        print(f"Threshold: {THRESHOLD}")
        print("="*50 + "\n")
        
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n✓ AI inference stopped")
        print_stats()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
