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