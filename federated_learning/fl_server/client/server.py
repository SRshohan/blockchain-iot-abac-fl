import flwr as fl
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from flwr.common import Metrics, Parameters, FitRes, EvaluateRes
from flwr.server.client_proxy import ClientProxy

# Create directory for server metrics
os.makedirs("server_metrics", exist_ok=True)

# Metrics tracking class for server
class ServerMetricsTracker:
    def __init__(self):
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "rounds": [],
            "clients": {},
            "global_metrics": []
        }
    
    def log_round_start(self, rnd: int):
        """Log the start of a federated round"""
        round_metrics = {
            "round": rnd,
            "start_time": datetime.now().isoformat(),
            "client_metrics": [],
            "aggregated_metrics": {}
        }
        self.metrics["rounds"].append(round_metrics)
    
    def log_fit_metrics(self, rnd: int, results, client_ids):
        """Log metrics from client fit results"""
        # Get the current round metrics
        round_metrics = self.metrics["rounds"][-1]
        
        # Process each client's results
        for idx, (fit_res, client_id) in enumerate(zip(results, client_ids)):
            # Extract metrics
            num_examples = fit_res.num_examples
            metrics = fit_res.metrics if fit_res.metrics else {}
            
            # Log client metrics
            client_data = {
                "client_id": client_id,
                "num_examples": num_examples,
                "metrics": metrics
            }
            round_metrics["client_metrics"].append(client_data)
            
            # Update client history
            if client_id not in self.metrics["clients"]:
                self.metrics["clients"][client_id] = []
            
            self.metrics["clients"][client_id].append({
                "round": rnd,
                "fit_metrics": metrics,
                "num_examples": num_examples
            })
    
    def log_evaluate_metrics(self, rnd: int, results, client_ids):
        """Log metrics from client evaluation results"""
        # Get the current round metrics
        round_metrics = self.metrics["rounds"][-1]
        
        evaluation_metrics = []
        accuracies = []
        losses = []
        
        # Process each client's results
        for idx, (eval_res, client_id) in enumerate(zip(results, client_ids)):
            # Extract metrics
            loss = eval_res.loss
            num_examples = eval_res.num_examples
            metrics = eval_res.metrics if eval_res.metrics else {}
            
            # Extract accuracy if available
            accuracy = metrics.get("accuracy", 0.0)
            
            # Append to lists for aggregate calculations
            if loss is not None:
                losses.append(loss)
            if accuracy is not None:
                accuracies.append(accuracy)
            
            # Log evaluation metrics
            evaluation_data = {
                "client_id": client_id,
                "loss": loss,
                "num_examples": num_examples,
                "metrics": metrics
            }
            evaluation_metrics.append(evaluation_data)
            
            # Update client history
            if client_id in self.metrics["clients"]:
                client_history = next((h for h in self.metrics["clients"][client_id] if h["round"] == rnd), None)
                if client_history:
                    client_history["evaluation"] = {
                        "loss": loss,
                        "metrics": metrics
                    }
        
        # Calculate and save aggregate metrics
        if losses:
            round_metrics["aggregated_metrics"]["mean_loss"] = float(np.mean(losses))
            round_metrics["aggregated_metrics"]["std_loss"] = float(np.std(losses))
        
        if accuracies:
            round_metrics["aggregated_metrics"]["mean_accuracy"] = float(np.mean(accuracies))
            round_metrics["aggregated_metrics"]["std_accuracy"] = float(np.std(accuracies))
        
        # Add evaluation metrics to the round
        round_metrics["evaluation_metrics"] = evaluation_metrics
        
        # Add global metrics
        self.metrics["global_metrics"].append({
            "round": rnd,
            "timestamp": datetime.now().isoformat(),
            "mean_loss": round_metrics["aggregated_metrics"].get("mean_loss"),
            "mean_accuracy": round_metrics["aggregated_metrics"].get("mean_accuracy")
        })
    
    def log_round_end(self, rnd: int):
        """Log the end of a federated round"""
        # Get the current round metrics
        round_metrics = self.metrics["rounds"][-1]
        round_metrics["end_time"] = datetime.now().isoformat()
        
        # Calculate round duration
        start = datetime.fromisoformat(round_metrics["start_time"])
        end = datetime.fromisoformat(round_metrics["end_time"])
        round_metrics["duration_seconds"] = (end - start).total_seconds()
        
        # Save metrics after each round
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to a JSON file"""
        filename = "server_metrics/server_metrics.json"
        with open(filename, 'w') as f:
            json.dump(self.metrics, f, indent=2)

# Create metrics tracker
server_metrics = ServerMetricsTracker()

# Function to get client IDs
def get_client_id(client_proxy: ClientProxy) -> str:
    """Extract client ID from client proxy."""
    return f"client_{client_proxy.cid}"

# Custom strategy with callbacks for metrics tracking
class MetricsStrategy(fl.server.strategy.FedAvg):
    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Metrics]]:
        # Log round start
        server_metrics.log_round_start(server_round)
        
        # Extract client IDs
        client_ids = [get_client_id(client) for client, _ in results]
        
        # Log fit metrics
        fit_results = [fit_res for _, fit_res in results]
        server_metrics.log_fit_metrics(server_round, fit_results, client_ids)
        
        # Aggregate parameters and metrics using the parent method
        parameters, metrics = super().aggregate_fit(server_round, results, failures)
        
        return parameters, metrics
    
    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Metrics]]:
        # Extract client IDs
        client_ids = [get_client_id(client) for client, _ in results]
        
        # Log evaluation metrics
        eval_results = [eval_res for _, eval_res in results]
        print(eval_results)
        server_metrics.log_evaluate_metrics(server_round, eval_results, client_ids)
        
        # Aggregate loss and metrics using the parent method
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)
        
        # Log round end
        server_metrics.log_round_end(server_round)
        
        return loss, metrics

# Define fit configuration to send to clients
def fit_config(server_round: int):
    """Return training configuration dict for each round."""
    config = {
        "batch_size": 32,
        "epochs": 15,
        "round": server_round,
    }
    return config

def evaluate_config(server_round: int):
    """Return evaluation configuration dict for each round."""
    return {"round": server_round}

# Create an instance of the custom strategy
strategy = MetricsStrategy(
    min_available_clients=2,
)

# Start the server
if __name__ == "__main__":
    try:
        # Start the server
        fl.server.start_server(
            server_address="127.0.0.1:8080",
            config=fl.server.ServerConfig(num_rounds=1),
            strategy=strategy
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nServer shutdown complete")