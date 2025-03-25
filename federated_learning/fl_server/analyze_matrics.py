import json
import glob
import matplotlib.pyplot as plt
import numpy as np

def analyze_client_metrics(metrics_dir="client_metrics/"):
    # Find all metric files
    metrics_files = glob.glob(metrics_dir + "*.json")
    
    all_metrics = []
    for file_path in metrics_files:
        with open(file_path, 'r') as f:
            metrics = json.load(f)
            all_metrics.append(metrics)
    
    # Extract metrics for plotting
    rounds = []
    accuracies = []
    losses = []
    
    for metrics in all_metrics:
        for round_data in metrics["training_rounds"]:
            rounds.append(round_data["round"])
            accuracies.append(round_data["accuracy"])
            losses.append(round_data["loss"])
    
    # Create plots
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.scatter(rounds, accuracies)
    plt.title("Accuracy across training rounds")
    plt.xlabel("Round")
    plt.ylabel("Accuracy")
    
    plt.subplot(1, 2, 2)
    plt.scatter(rounds, losses)
    plt.title("Loss across training rounds")
    plt.xlabel("Round")
    plt.ylabel("Loss")
    
    plt.tight_layout()
    plt.savefig("federated_metrics_analysis.png")
    plt.show()
    
if __name__ == "__main__":
    analyze_client_metrics()