# Setup Guide: Blockchain-ABAC-FL Integration for IoT

This guide outlines steps to set up the development environment on **macOS** and deploy the system on **Raspberry Pi (RPi)** for testing with real IoT sensors.

---

## Prerequisites

### Hardware
- macOS machine (for development)
- Raspberry Pi (4B or newer recommended)
- IoT sensors (e.g., DHT11/DHT22 for temperature/humidity, PIR motion sensor, camera module)
- Breadboard, jumper wires, resistors (for sensor connections)

### Software
- macOS Terminal or iTerm2
- Xcode Command Line Tools (for macOS dependencies)
- Python 3.8+ and Node.js 16.x (LTS)
- Docker Desktop for macOS
- Raspberry Pi OS (64-bit) installed on RPi SD card

---

## Part 1: macOS Development Setup

### 1. Install Dependencies
```bash
# Install Homebrew (package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Node.js, and tools
brew install python@3.10 node git docker docker-compose

# Install Python virtualenv
pip3 install virtualenv

# Install Hyperledger Fabric dependencies (for permissioned blockchain)
brew install curl openssl
```

2. Set Up Blockchain Network (Hyperledger Fabric)

```bash
# Create a project directory
mkdir iot-blockchain && cd iot-blockchain

# Clone Hyperledger Fabric samples (simplified setup)
git clone https://github.com/hyperledger/fabric-samples.git

cd fabric-samples/test-network

# Start a minimal Fabric network (adjust as needed)
./network.sh up createChannel -c mychannel -s couchdb
```

3. Install Privacy-Preserving Libraries
```bash
# Create a Python virtual environment
virtualenv venv && source venv/bin/activate

# Install federated learning and privacy tools
pip install syft==0.8.0 tensorflow-federated tensorflow==2.12.0 \diffprivlib torch torchvision
```

### Reference Setup Diagram
┌───────────────────┐       ┌──────────────────────────┐
│ Raspberry Pi      │       │ Hyperledger Fabric       │
│ (IoT Device)      │       │ (Server/Cloud)           │
│                   │       │                          │
│  - Sensor (DHT11) │──────▶│  - Peer Nodes            │
│  - ABAC Client    │ REST/ │  - Orderer               │
│  - FL Client      │ gRPC  │  - Chaincode (ABAC/FL)   │
└───────────────────┘       └──────────────────────────┘




### Path to Dataset
```sh
/Users/sohanurrahman/.cache/kagglehub/datasets/jessicali9530/celeba-dataset/versions/2
```