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

### General Step
Register identities with attributes:

```bash
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org1.example.com/
```

Step 1: For registration
```bash
fabric-ca-client register --id.name creator3 --id.secret creator1pw --id.type client --id.affiliation org1 --id.attrs 'abac.location=home1:ecert, abac.time=14001900' --tls.certfiles "${PWD}/organizations/fabric-ca/org1/tls-cert.pem"
```


Step 2: For Enrollment: 
```bash
fabric-ca-client enroll -u https://creator3:creator1pw@localhost:7054 --caname ca-org1 -M "${PWD}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp" --tls.certfiles "${PWD}/organizations/fabric-ca/org1/tls-cert.pem"
```

Step 3: Copy it
```bash
cp "${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml" "${PWD}/organizations/peerOrganizations/org1.example.com/users/creator1@org1.example.com/msp/config.yaml"
```