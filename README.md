# Hyperledger Fabric ABAC Based Access For Different User 🔒⛓️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FireFly Version](https://img.shields.io/badge/FireFly-1.2.0-blue)](https://hyperledger.github.io/firefly/)

A secure asset management system implementing Attribute-Based Access Control (ABAC) using Hyperledger Fabric and FireFly. Manages device assets with granular permissions through blockchain smart contracts.

![Network Demo](https://media.giphy.com/media/cF2ITQKdxDUChJlYRx/giphy.gif?cid=790b76117663sbo8hjd4vsuqa28yf752zos1t3se8rg4yrgr&ep=v1_gifs_search&rid=giphy.gif&ct=g) 
*(Example: Network Startup & Chaincode Deployment)*

## Features ✨
- ABAC implementation with custom attributes
- CouchDB state database for rich queries
- FireFly integration for REST APIs
- Multi-organization channel setup
- Attribute-based asset creation rules

## Prerequisites 📋
- [Hyperledger Fabric Samples v2.4+](https://github.com/hyperledger/fabric-samples)
- [FireFly CLI v1.2+](https://hyperledger.github.io/firefly/)
- Docker 20.10+
- Node.js 16.x
- Go 1.18+

## Installation ⚙️
```bash
git clone https://github.com/SRshohan/blockchain-iot-abac-fl.git
cd blockchain-iot-abac-fl
```

```sh
Examples:
   network.sh up createChannel -ca -c mychannel -s couchdb
   network.sh createChannel -c channelName
   network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
   network.sh deployCC -ccn mychaincode -ccp ./user/mychaincode -ccv 1 -ccl javascript

```

### Notes

```sh
openssl x509 -in cert.pem -text -noout

```


### Instead of Go use javascript ( because needs to run the module first)

```bash
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript -ccl javascript
```

# Facing error
```sh
Error: error getting endorser client for channel: endorser client failed to connect to localhost:7051: failed to create new connection: context deadline exceeded
After 5 attempts, peer0.org1 has failed to join channel 'mychannel'
```



Solution:

```bash
# Tear down any existing containers/volumes
./network.sh down
docker system prune -a --volumes

# Bring the network back up
./network.sh up createChannel -s couchdb
```

```sh
./network.sh deployCC -ccn ledger -ccp ../asset-transfer-ledger-queries/chaincode-javascript/ -ccl javascript -ccep "OR('Org1MSP.peer','Org2MSP.peer')"
```

## Follow the step
### Start the network and Deploy the chaincode
```sh
./network.sh up createChannel -ca
./network.sh deployCC -ccn abac -ccp ../asset-transfer-abac/chaincode-go/ -ccl go
```

### General Step for ABAC

FireUp the network & Deploy the Chaincode:
```sh
./network.sh up createChannel -ca -s couchdb
./network.sh deployCC -ccn abac -ccp ../asset-transfer-abac/chaincode-go/ -ccl go
```

1. Setup Environment Variables to Setup Fabric CA Client:
```sh
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
```

2. Setup Fabric CA client home to the MSP of the Org1 CA admin:
```bash
export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org1.example.com/
```

### Register identities with attributes

1. Step 1: For registration
```bash
fabric-ca-client register --id.name creator3 --id.secret creator1pw --id.type client --id.affiliation org1 --id.attrs 'abac.location=home1backyard:ecert,abac.creator=true:ecert,abac.status=true:ecert' --tls.certfiles "${PWD}/organizations/fabric-ca/org1/tls-cert.pem"
```

Step 2: For Enrollment: 
```bash
fabric-ca-client enroll -u https://creator3:creator1pw@localhost:7054 --caname ca-org1 -M "${PWD}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp" --tls.certfiles "${PWD}/organizations/fabric-ca/org1/tls-cert.pem"
```

1. Step 3: Copy it
```bash
cp "${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml" "${PWD}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp/config.yaml"
```

#### Use an User Identity to Create a Asset

1. Set Up Environment Variables for User Identity

```bash
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=localhost:7051
export TARGET_TLS_OPTIONS=(-o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt")
```

2. Run to invoke Specific Chaincode Function (eg: CreateDeviceAsset):

```bash
peer chaincode invoke "${TARGET_TLS_OPTIONS[@]}" -C mychannel -n abac -c '{"function":"CreateDeviceAsset","Args":["device1", "home1", "true"]}'
```

3. Decode certificate using Openssl

```bash
openssl x509 -in organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp/signcerts/cert.pem -text -noout
```

## Todo

Checkout the FireFly with fabric-samples test-network

[FireFly](https://hyperledger.github.io/firefly/latest/tutorials/chains/fabric_test_network/#start-firefly-stack)


## install firefly

### Initialize and setup Firefly
Make sure to use the right port, The default port is 5000 and default channel is firefly which automatically setup in firefly config

```bash
ff init fabric dev -p  5006 --channel firefly --chaincode asset_transfer
```

### Start the FireFly
```bash
ff start dev
```

#### Remove the dev and Stop the dev

```bash
ff remove dev
```

```bash
ff stop dev
```

### Zip the chaincode
To use the chaincode from the Fabric-samples need the Following setup:

```bash
cd fabric-samples/asset-transfer-basic/chaincode-go
touch core.yaml
peer lifecycle chaincode package -p . --label asset_transfer ./asset_transfer.zip
```

Make sure to activate `peer` from `test-network`. To do that we need to set those Environment variables:

```bash
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
```

### Deploy Chaincode
```bash
ff deploy fabric dev asset_transfer.zip firefly asset_transfer 1.0
```

### Follow steps to create the following

Go to the UI link for FireFly Sandbox: `http://127.0.0.1:5108`

- Go to the `Contracts` Section
- Click on Define a `Contract Interface`
- Select `FFI - FireFly` Interface in the `Interface Fromat` dropdown
- Copy the `FFI JSON` crafted by you into the `Schema` Field
- Click on `Run`

```bash
{
  "namespace": "default",
  "name": "asset_transfer",
  "description": "Spec interface for the asset-transfer-basic golang chaincode",
  "version": "1.0",
  "methods": [
    {
      "name": "GetAllAssets",
      "pathname": "",
      "description": "",
      "params": [],
      "returns": [
        {
          "name": "",
          "schema": {
            "type": "array",
            "details": {
              "type": "object",
              "properties": {
                "type": "string"
              }
            }
          }
        }
      ]
    },
    {
      "name": "CreateAsset",
      "pathname": "",
      "description": "",
      "params": [
        {
          "name": "id",
          "schema": {
            "type": "string"
          }
        },
        {
          "name": "color",
          "schema": {
            "type": "string"
          }
        },
        {
          "name": "size",
          "schema": {
            "type": "string"
          }
        },
        {
          "name": "owner",
          "schema": {
            "type": "string"
          }
        },
        {
          "name": "value",
          "schema": {
            "type": "string"
          }
        }
      ],
      "returns": []
    }
  ],
  "events": [
    {
      "name": "AssetCreated"
    }
  ]
}

```

#### Create an HTTP API for the contract
Create this Http API: `http://127.0.0.1:5108`

- Go to the `Contracts` Section
- Click on `Register a Contract API`
- Select the `name` of your broadcasted FFI in the `Contract Interface` dropdown
- In the `Name` Field, give a name that will be part of the URL for your Http API
- In the `Chaincode` Field, give your `chaincode name` for which you wrote the FFI
- In the `Channel` Field, give the channel name where your `chaincode` is deployed
- Click on `Run`

### Check from THE FIREFLY UI

Follow the link: `http://127.0.0.1:5007/ui`

- Go to `Blockchain`
- Then Go to `API`

Then check the link

### Invoke the chaincode
Now that we've got everything set up, it's time to use our chaincode! We're going to make a POST request to the `invoke/CreateAsset` endpoint to create a new asset.

Request
POST `http://localhost:5000/api/v1/namespaces/default/apis/asset_transfer/invoke/CreateAsset`


```bash
{
  "input": {
    "color": "blue",
    "id": "asset-01",
    "owner": "Harry",
    "size": "30",
    "value": "23400"
  }
}
```

Contribution