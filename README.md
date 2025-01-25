```sh
blockchain-iot-abac-fl/  
├── blockchain/                 # Blockchain network setup (Hyperledger Fabric)  
│   ├── chaincode/              # Smart contracts for ABAC policies  
│   └── config/                 # Network configuration files  
├── abac-policies/              # XACML/JSON attribute-based policies  
│   ├── smart_home_policies.xacml  
│   └── policy_enforcer.py      # AuthZForce/OpenPolicyAgent integration  
├── federated-learning/         # FL client/server code  
│   ├── clients/                # IoT device code (Raspberry Pi/ESP32)  
│   │   ├── dp_noise.py         # Differential privacy module  
│   │   └── local_train.py      # Local model training script  
│   └── aggregator/             # Blockchain/Edge-based aggregation logic  
├── testbed-simulation/         # Hardware/IoT device simulations  
│   ├── docker-compose.yml      # Simulate IoT nodes  
│   └── sensor_data/            # Sample datasets (N-BaIoT, CASAS)  
├── docs/                       # Research papers, diagrams, test plans  
├── scripts/                    # Utility scripts (deployment, monitoring)  
├── .github/                    # CI/CD workflows (e.g., automated testing)  
├── requirements.txt            # Python dependencies  
├── Dockerfile                  # Containerized testbed setup  
└── README.md                   # Project overview, setup instructions  
```