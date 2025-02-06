package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

type UserAttributes struct{
	ID string 
	Name string
	Role string
	Condition map[string]string
	UsageLimits int
	Location [3]string
	Status bool
	Creator string
	
}



func (s *SmartContract) CreateUser (ctx contractapi.TransactionContext, ){
	
}




