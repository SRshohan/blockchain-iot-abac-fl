Examples:
   network.sh up createChannel -ca -c mychannel -s couchdb
   network.sh createChannel -c channelName
   network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
   network.sh deployCC -ccn mychaincode -ccp ./user/mychaincode -ccv 1 -ccl javascript



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