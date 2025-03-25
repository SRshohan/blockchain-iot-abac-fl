import flwr as fl


strategy = fl.server.strategy.FedAvg(
    min_available_clients=2,
    min_evaluate_clients=2, 
    min_fit_clients=2
)


fl.server.start_server(
    server_address="192.168.1.14:8080",
    config=fl.server.ServerConfig(num_rounds=3),
    strategy=strategy,
)