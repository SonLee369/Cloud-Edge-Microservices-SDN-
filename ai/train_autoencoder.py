#!/usr/bin/env python3
"""
Autoencoder Training Script for ECG Anomaly Detection
Collects normal ECG data and trains the model to recognize normal patterns
"""
import numpy as np
import json
import time
import paho.mqtt.client as mqtt
from collections import deque
from datetime import datetime
import pickle

# Configuration
MQTT_BROKER = "localhost"
MQTT_TOPIC = "healthcare/ecg/#"
WINDOW_SIZE = 10
TRAINING_SAMPLES = 5000  # Collect 5000 normal samples for training
EPOCHS = 50
LEARNING_RATE = 0.01
MODEL_FILE = "autoencoder_weights.pkl"

# Autoencoder Model
class AutoencoderTrainer:
    """Trainable autoencoder for ECG patterns"""
    
    def __init__(self, input_dim=10):
        self.input_dim = input_dim
        # Initialize with small random weights
        np.random.seed(42)
        self.encoder_w1 = np.random.randn(input_dim, 6) * 0.1
        self.encoder_b1 = np.zeros(6)
        self.decoder_w1 = np.random.randn(6, input_dim) * 0.1
        self.decoder_b1 = np.zeros(input_dim)
        
        # For Adam optimizer
        self.m_ew1 = np.zeros_like(self.encoder_w1)
        self.v_ew1 = np.zeros_like(self.encoder_w1)
        self.m_eb1 = np.zeros_like(self.encoder_b1)
        self.v_eb1 = np.zeros_like(self.encoder_b1)
        self.m_dw1 = np.zeros_like(self.decoder_w1)
        self.v_dw1 = np.zeros_like(self.decoder_w1)
        self.m_db1 = np.zeros_like(self.decoder_b1)
        self.v_db1 = np.zeros_like(self.decoder_b1)
        self.t = 0
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)
    
    def forward(self, x, return_intermediate=False):
        """Forward pass"""
        # Encoder
        z1 = np.dot(x, self.encoder_w1) + self.encoder_b1
        a1 = self.relu(z1)
        
        # Decoder
        z2 = np.dot(a1, self.decoder_w1) + self.decoder_b1
        a2 = self.sigmoid(z2)
        
        if return_intermediate:
            return a2, (z1, a1, z2)
        return a2
    
    def backward(self, x, intermediates):
        """Backward pass with gradient descent"""
        z1, a1, z2 = intermediates
        reconstruction = self.sigmoid(z2)
        
        # Output layer gradients
        delta2 = (reconstruction - x) * self.sigmoid_derivative(z2)
        grad_dw1 = np.dot(a1.T, delta2)
        grad_db1 = np.sum(delta2, axis=0)
        
        # Hidden layer gradients
        delta1 = np.dot(delta2, self.decoder_w1.T) * self.relu_derivative(z1)
        grad_ew1 = np.dot(x.T, delta1)
        grad_eb1 = np.sum(delta1, axis=0)
        
        return grad_ew1, grad_eb1, grad_dw1, grad_db1
    
    def adam_update(self, grads, lr=0.01, beta1=0.9, beta2=0.999, eps=1e-8):
        """Adam optimizer update"""
        self.t += 1
        grad_ew1, grad_eb1, grad_dw1, grad_db1 = grads
        
        # Update encoder weights
        self.m_ew1 = beta1 * self.m_ew1 + (1 - beta1) * grad_ew1
        self.v_ew1 = beta2 * self.v_ew1 + (1 - beta2) * (grad_ew1 ** 2)
        m_hat = self.m_ew1 / (1 - beta1 ** self.t)
        v_hat = self.v_ew1 / (1 - beta2 ** self.t)
        self.encoder_w1 -= lr * m_hat / (np.sqrt(v_hat) + eps)
        
        self.m_eb1 = beta1 * self.m_eb1 + (1 - beta1) * grad_eb1
        self.v_eb1 = beta2 * self.v_eb1 + (1 - beta2) * (grad_eb1 ** 2)
        m_hat = self.m_eb1 / (1 - beta1 ** self.t)
        v_hat = self.v_eb1 / (1 - beta2 ** self.t)
        self.encoder_b1 -= lr * m_hat / (np.sqrt(v_hat) + eps)
        
        # Update decoder weights
        self.m_dw1 = beta1 * self.m_dw1 + (1 - beta1) * grad_dw1
        self.v_dw1 = beta2 * self.v_dw1 + (1 - beta2) * (grad_dw1 ** 2)
        m_hat = self.m_dw1 / (1 - beta1 ** self.t)
        v_hat = self.v_dw1 / (1 - beta2 ** self.t)
        self.decoder_w1 -= lr * m_hat / (np.sqrt(v_hat) + eps)
        
        self.m_db1 = beta1 * self.m_db1 + (1 - beta1) * grad_db1
        self.v_db1 = beta2 * self.v_db1 + (1 - beta2) * (grad_db1 ** 2)
        m_hat = self.m_db1 / (1 - beta1 ** self.t)
        v_hat = self.v_db1 / (1 - beta2 ** self.t)
        self.decoder_b1 -= lr * m_hat / (np.sqrt(v_hat) + eps)
    
    def train_batch(self, X, lr=0.01):
        """Train on a batch"""
        reconstruction, intermediates = self.forward(X, return_intermediate=True)
        grads = self.backward(X, intermediates)
        self.adam_update(grads, lr)
        
        # Calculate loss
        mse = np.mean((X - reconstruction) ** 2)
        return mse
    
    def save_weights(self, filename):
        """Save trained weights"""
        weights = {
            'encoder_w1': self.encoder_w1,
            'encoder_b1': self.encoder_b1,
            'decoder_w1': self.decoder_w1,
            'decoder_b1': self.decoder_b1
        }
        with open(filename, 'wb') as f:
            pickle.dump(weights, f)
        print(f"✓ Model saved to {filename}")

# Data collection
normal_data = []
data_buffer = deque(maxlen=WINDOW_SIZE)

def on_message(client, userdata, msg):
    """Collect normal ECG data only"""
    global normal_data
    
    try:
        data = json.loads(msg.payload.decode())
        value = data.get('value', 0)
        is_anomaly = data.get('anomaly_injected', False)
        
        # Only collect NORMAL data for training
        if not is_anomaly:
            data_buffer.append(value)
            
            if len(data_buffer) == WINDOW_SIZE:
                normal_data.append(list(data_buffer))
                
                if len(normal_data) % 100 == 0:
                    print(f"Collected {len(normal_data)} normal samples...")
                
                if len(normal_data) >= TRAINING_SAMPLES:
                    client.disconnect()
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    print("="*60)
    print("AUTOENCODER TRAINING PIPELINE")
    print("="*60)
    print(f"Target samples: {TRAINING_SAMPLES}")
    print(f"Window size: {WINDOW_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print("="*60)
    
    # Step 1: Collect normal data
    print("\n[1/3] Collecting normal ECG data...")
    print("Make sure ECG simulator is running!")
    
    client = mqtt.Client()
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, 1883, 60)
        client.subscribe(MQTT_TOPIC)
        print(f"✓ Connected to MQTT broker")
        
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n⚠ Collection interrupted by user")
    except Exception as e:
        print(f"ERROR: {e}")
    
    if len(normal_data) < 100:
        print(f"\n❌ Not enough data collected ({len(normal_data)} samples)")
        print("Make sure the ECG simulator is running!")
        return
    
    print(f"✓ Collected {len(normal_data)} normal samples")
    
    # Step 2: Train the model
    print(f"\n[2/3] Training autoencoder...")
    X_train = np.array(normal_data)
    
    model = AutoencoderTrainer(input_dim=WINDOW_SIZE)
    
    for epoch in range(EPOCHS):
        # Shuffle data
        indices = np.random.permutation(len(X_train))
        X_shuffled = X_train[indices]
        
        # Train in mini-batches
        batch_size = 32
        losses = []
        
        for i in range(0, len(X_shuffled), batch_size):
            batch = X_shuffled[i:i+batch_size]
            loss = model.train_batch(batch, lr=LEARNING_RATE)
            losses.append(loss)
        
        avg_loss = np.mean(losses)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.6f}")
    
    print(f"✓ Training complete! Final loss: {avg_loss:.6f}")
    
    # Step 3: Save the model
    print(f"\n[3/3] Saving trained weights...")
    model.save_weights(MODEL_FILE)
    
    # Calculate reconstruction error distribution
    reconstructions = model.forward(X_train)
    errors = np.mean((X_train - reconstructions) ** 2, axis=1)
    
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Training samples: {len(normal_data)}")
    print(f"Final MSE loss: {avg_loss:.6f}")
    print(f"\nReconstruction Error Statistics (Normal Data):")
    print(f"  Mean:   {np.mean(errors):.4f}")
    print(f"  Std:    {np.std(errors):.4f}")
    print(f"  95th percentile: {np.percentile(errors, 95):.4f}")
    print(f"\nRecommended threshold: {np.percentile(errors, 95) + 0.1:.4f}")
    print(f"(Set threshold above 95th percentile to detect anomalies)")
    print("="*60)

if __name__ == "__main__":
    main()
