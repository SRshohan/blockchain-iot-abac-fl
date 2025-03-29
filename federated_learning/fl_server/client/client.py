import tensorflow as tf
import flwr as fl
import ssl
import numpy as np
import os
import json
from datetime import datetime
import psutil
import threading
import time
import platform
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource

# For SSL certificate issues
ssl._create_default_https_context = ssl._create_unverified_context

# Create directories for metrics
os.makedirs("client_metrics", exist_ok=True)
os.makedirs("resource_metrics", exist_ok=True)

# Client ID - unique for each device
CLIENT_ID = input("Enter client ID: ")
location = input("Enter location: ")
timezone = time.time()

# Function to get client information
def client_info():
    return{
        "client_id": CLIENT_ID,
        "location": location,
        "timezone": timezone,
        "status"  : "active"
    }

class sendData(Resource):
    def post(self, data):
        print(data)
        return jsonify(data)
app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(sendData, '/sendData')

app.run(host='0.0.0.0', port=5000)



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

# Resource monitoring class
class ResourceMonitor:
    def __init__(self, client_id, interval=1.0):
        self.client_id = client_id
        self.interval = interval
        self.running = False
        self.thread = None
        self.resource_data = []
        self.current_round = 0
        self.round_start_time = None
        
    def _get_system_info(self):
        """Get static system information"""
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "tf_version": tf.__version__,
            "cpu_count": psutil.cpu_count(logical=True)
        }
        
    def start_monitoring(self, round_num=0):
        """Start resource monitoring in a separate thread"""
        self.running = True
        self.current_round = round_num
        self.round_start_time = time.time()
        self.resource_data = []
        
        def monitor_resources():
            start_time = time.time()
            
            while self.running:
                # Collect CPU, memory, disk, and network metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net = psutil.net_io_counters()
                
                # Store metrics with timestamp
                self.resource_data.append({
                    "timestamp": time.time() - start_time,
                    "round": self.current_round,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_mb": memory.used / (1024 * 1024),
                    "disk_percent": disk.percent,
                    "network_sent_mb": net.bytes_sent / (1024 * 1024),
                    "network_recv_mb": net.bytes_recv / (1024 * 1024)
                })
                
                # Print current resource usage
                print(f"\r[Resource Monitor] Round {self.current_round} - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%", end="")
                
                time.sleep(self.interval)
        
        self.thread = threading.Thread(target=monitor_resources)
        self.thread.daemon = True
        self.thread.start()
        print(f"Resource monitoring started for round {round_num}")
    
    def stop_monitoring(self):
        """Stop resource monitoring and save the data"""
        if not self.running:
            return
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        # Save the resource data
        if self.resource_data:
            round_duration = time.time() - self.round_start_time
            
            # Save data to file
            filename = f"resource_metrics/resources_round_{self.current_round}_{self.client_id}.json"
            with open(filename, 'w') as f:
                json.dump({
                    "client_id": self.client_id,
                    "round": self.current_round,
                    "system_info": self._get_system_info(),
                    "round_duration_seconds": round_duration,
                    "resource_data": self.resource_data
                }, f, indent=2)
                
            print(f"\nResource monitoring stopped. Data saved to {filename}")

# Create resource monitor
resource_monitor = ResourceMonitor(CLIENT_ID)

# Metrics tracking class
class MetricsTracker:
    def __init__(self, client_id):
        self.client_id = client_id
        self.metrics = {
            "client_id": client_id,
            "rounds": [],
            "system_info": self._get_system_info()
        }
    
    def _get_system_info(self):
        """Get system information from the device"""
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
        
        # Start resource monitoring
        resource_monitor.start_monitoring(current_round)
        
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
        
        try:
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
            
        finally:
            # Stop resource monitoring (even if there's an error)
            resource_monitor.stop_monitoring()
        
        # Complete round logging
        tracker.log_round_end()
        
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

if __name__ == "__main__":
    try:
        # Start Flower client
        fl.client.start_numpy_client(
            server_address="127.0.0.1:8080",
            client=CifarClient()
        )


    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Make sure resource monitoring is stopped
        if hasattr(resource_monitor, 'running') and resource_monitor.running:
            resource_monitor.stop_monitoring()