import tensorflow as tf
import flwr as fl
import ssl
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

# For SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

# Create directories for metrics
os.makedirs("client_metrics", exist_ok=True)

# Client ID - unique for each device
CLIENT_ID = input("Enter client ID: ")  # Change for each Raspberry Pi

# Define and compile the model
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])
model.compile(
    'adam',
    "sparse_categorical_crossentropy",
    metrics=['accuracy']
)

# Load dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
# Normalize data
x_train, x_test = x_train / 255.0, x_test / 255.0

# Metrics tracking class
class MetricsTracker:
    def __init__(self, client_id):
        self.client_id = client_id
        self.metrics = {
            "client_id": client_id,
            "rounds": [],
            "system_info": self._get_system_info(),
            "training_history": []
        }
    
    def _get_system_info(self):
        """Get system information from the device"""
        import platform
        import psutil
        
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "tf_version": tf.__version__
        }
    
    def log_round_start(self, round_num):
        """Log the start of a training round"""
        self.current_round = {
            "round_num": round_num,
            "start_time": datetime.now().isoformat(),
            "metrics": {}
        }
    
    def log_training_history(self, history):
        """Log training history from model.fit"""
        # Convert history to regular dict with list values
        history_dict = {}
        for key, value in history.history.items():
            history_dict[key] = [float(v) for v in value]
        
        # Add to current round
        self.current_round["training_history"] = history_dict
        
        # Save training curves
        self._plot_training_curves(history_dict, self.current_round["round_num"])
    
    def log_evaluation(self, loss, accuracy):
        """Log evaluation results"""
        self.current_round["metrics"]["evaluation"] = {
            "loss": float(loss),
            "accuracy": float(accuracy)
        }
    
    def log_round_end(self):
        """Complete the round and add to metrics history"""
        self.current_round["end_time"] = datetime.now().isoformat()
        
        # Calculate training time
        start = datetime.fromisoformat(self.current_round["start_time"])
        end = datetime.fromisoformat(self.current_round["end_time"])
        self.current_round["training_time_seconds"] = (end - start).total_seconds()
        
        # Add to rounds history
        self.metrics["rounds"].append(self.current_round)
        
        # Save metrics after each round
        self._save_metrics()
    
    def _plot_training_curves(self, history, round_num):
        """Generate and save training curve plots"""
        plt.figure(figsize=(12, 5))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(history['accuracy'])
        plt.title(f'Model Accuracy - Round {round_num}')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(history['loss'])
        plt.title(f'Model Loss - Round {round_num}')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        
        plt.tight_layout()
        
        # Save the plot
        plots_dir = f"client_metrics/plots_{self.client_id}"
        os.makedirs(plots_dir, exist_ok=True)
        plt.savefig(f"{plots_dir}/round_{round_num}_training.png")
        plt.close()
    
    def _save_metrics(self):
        """Save metrics to a JSON file"""
        filename = f"client_metrics/metrics_{self.client_id}.json"
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)

# Create metrics tracker
tracker = MetricsTracker(CLIENT_ID)

# Global round counter
current_round = 0

class CifarClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return model.get_weights()
    
    def fit(self, parameters, config):
        global current_round
        current_round += 1
        
        # Log round start
        tracker.log_round_start(current_round)
        
        # Set model parameters
        model.set_weights(parameters)
        
        # Custom callback to track per-batch metrics
        class BatchMetricsCallback(tf.keras.callbacks.Callback):
            def __init__(self):
                super().__init__()
                self.batch_logs = []
            
            def on_batch_end(self, batch, logs=None):
                self.batch_logs.append({
                    'batch': batch,
                    'loss': float(logs['loss']),
                    'accuracy': float(logs['accuracy'])
                })
        
        # Create callback
        batch_metrics = BatchMetricsCallback()
        
        # Train the model and capture history
        history = model.fit(
            x_train, y_train,
            epochs=10,
            batch_size=8,
            verbose=1,
            callbacks=[batch_metrics]
        )
        
        # Log training history
        tracker.log_training_history(history)
        
        # Add batch-level metrics
        tracker.current_round["batch_metrics"] = batch_metrics.batch_logs
        
        # Complete round logging
        tracker.log_round_end()

        system = tracker._get_system_info()
        print(f"System info: {system}")
        
        # Return updated model parameters
        return model.get_weights(), len(x_train), {}
    
    def evaluate(self, parameters, config):
        # Set model parameters
        model.set_weights(parameters)
        
        # Evaluate the model
        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        
        # Log evaluation metrics
        tracker.log_evaluation(loss, accuracy)
        
        # Return evaluation results
        return loss, len(x_test), {"accuracy": accuracy}

# Start Flower client
fl.client.start_numpy_client(
    server_address="127.0.0.1:8080",
    client=CifarClient()
)