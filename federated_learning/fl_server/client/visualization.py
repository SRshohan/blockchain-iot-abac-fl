import json
import glob
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

def visualize_federated_results():
    # Create output directory
    os.makedirs("visualizations", exist_ok=True)
    
    # Load server metrics
    with open("server_metrics/server_metrics.json", "r") as f:
        server_metrics = json.load(f)
    
    # Find all client metrics files
    client_files = glob.glob("client_metrics/metrics_*.json")
    client_metrics = []
    
    for file in client_files:
        with open(file, "r") as f:
            client_metrics.append(json.load(f))
    
    # 1. Global Model Performance
    plt.figure(figsize=(12, 5))
    
    # Extract data
    rounds = [m["round"] for m in server_metrics["global_metrics"]]
    losses = [m["mean_loss"] for m in server_metrics["global_metrics"] if m["mean_loss"] is not None]
    accuracies = [m["mean_accuracy"] for m in server_metrics["global_metrics"] if m["mean_accuracy"] is not None]
    
    # Plot loss
    plt.subplot(1, 2, 1)
    plt.plot(rounds[:len(losses)], losses, 'o-', linewidth=2)
    plt.title('Global Model Loss Over Rounds', fontsize=14)
    plt.xlabel('Round', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Plot accuracy
    plt.subplot(1, 2, 2)
    plt.plot(rounds[:len(accuracies)], accuracies, 'o-', linewidth=2, color='green')
    plt.title('Global Model Accuracy Over Rounds', fontsize=14)
    plt.xlabel('Round', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("visualizations/global_performance.png", dpi=300)
    plt.close()
    
    # 2. Client Comparison
    if client_metrics:
        plt.figure(figsize=(14, 8))
        
        # Plot accuracy comparison
        plt.subplot(2, 1, 1)
        for i, client in enumerate(client_metrics):
            client_id = client["client_id"]
            round_data = []
            accuracies = []
            
            for round_info in client["rounds"]:
                if "metrics" in round_info and "evaluation" in round_info["metrics"]:
                    eval_metrics = round_info["metrics"]["evaluation"]
                    if "accuracy" in eval_metrics:
                        round_data.append(round_info["round_num"])
                        accuracies.append(eval_metrics["accuracy"])
            
            if round_data and accuracies:
                plt.plot(round_data, accuracies, 'o-', linewidth=2, label=f'Client {client_id}')
        
        plt.title('Client Accuracy Comparison', fontsize=14)
        plt.xlabel('Round', fontsize=12)
        plt.ylabel('Accuracy', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot training history for each client
        plt.subplot(2, 1, 2)
        for i, client in enumerate(client_metrics):
            client_id = client["client_id"]
            
            # Get the last round's training history
            if client["rounds"]:
                last_round = client["rounds"][-1]
                if "training_history" in last_round:
                    history = last_round["training_history"]
                    if "loss" in history:
                        epochs = list(range(1, len(history["loss"]) + 1))
                        plt.plot(epochs, history["loss"], '-', linewidth=2, 
                                 label=f'Client {client_id} (Round {last_round["round_num"]})')
        
        plt.title('Client Training Loss in Last Round', fontsize=14)
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel('Loss', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig("visualizations/client_comparison.png", dpi=300)
        plt.close()
    
    # 3. Create a heatmap showing per-client, per-round accuracy
    if client_metrics:
        # Collect data for heatmap
        client_ids = [client["client_id"] for client in client_metrics]
        max_round = max([r["round"] for r in server_metrics["global_metrics"]])
        
        # Create data matrix for heatmap
        heatmap_data = np.zeros((len(client_ids), max_round))
        
        # Fill in the data
        for i, client in enumerate(client_metrics):
            for round_info in client["rounds"]:
                if "metrics" in round_info and "evaluation" in round_info["metrics"]:
                    eval_metrics = round_info["metrics"]["evaluation"]
                    if "accuracy" in eval_metrics:
                        rnd = round_info["round_num"] - 1  # 0-based indexing
                        if 0 <= rnd < max_round:
                            heatmap_data[i, rnd] = eval_metrics["accuracy"]
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        
        # Custom colormap - white to blue
        cmap = LinearSegmentedColormap.from_list('blue_gradient', ['#f7fbff', '#08306b'])
        
        plt.imshow(heatmap_data, cmap=cmap, aspect='auto')
        plt.colorbar(label='Accuracy')
        plt.xlabel('Round', fontsize=12)
        plt.ylabel('Client', fontsize=12)
        plt.title('Accuracy Heatmap by Client and Round', fontsize=14)
        
        # Set x and y ticks
        plt.xticks(range(max_round), [i+1 for i in range(max_round)])
        plt.yticks(range(len(client_ids)), client_ids)
        
        # Add text annotations
        for i in range(len(client_ids)):
            for j in range(max_round):
                if heatmap_data[i, j] > 0:
                    plt.text(j, i, f'{heatmap_data[i, j]:.2f}', 
                             ha='center', va='center', 
                             color='white' if heatmap_data[i, j] > 0.5 else 'black')
        
        plt.tight_layout()
        plt.savefig("visualizations/accuracy_heatmap.png", dpi=200)
        plt.close()
    
    print("Visualizations generated in the 'visualizations' directory.")

if __name__ == "__main__":
    visualize_federated_results()