# Makefile for invoking chaincode using Fablo CLI

# Define variables for the command
PEERS = "peer0.org1.example.com"
CHANNEL = "my-channel1"
CHAINCODE = "chaincode1"
ARGS = '{"Args":["ABACchaincode:createAsset", "device123", "owner1", "TemperatureSensor", "Room1", "Active"]}'

# Target to invoke the createDevice function
invoke-create-device:
	@echo "Invoking createDevice function..."
	./fablo chaincode invoke $(PEERS) $(CHANNEL) $(CHAINCODE) $(ARGS)


