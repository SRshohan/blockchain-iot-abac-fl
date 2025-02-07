package main

import ("fmt"
		"github.com/hyperledger/fabric-contract-api-go/contractapi"
)


func main() {
	chaincode, err := contractapi.NewChaincode(new(SmartContract)) // This is the crucial line!
	if err != nil {
			fmt.Printf("Error create fabcar chaincode: %v", err)
			return
	}

	if err := chaincode.Start(); err != nil {
			fmt.Printf("Error starting fabcar chaincode: %v", err)
	}
}



