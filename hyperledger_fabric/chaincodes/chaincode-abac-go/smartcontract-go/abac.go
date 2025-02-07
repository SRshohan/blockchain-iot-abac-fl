package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
	"golang.org/x/tools/go/analysis/passes/nilfunc"
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
}

type DeviceAttributes struct{
	ID string
	Location string
	OperationalStatus bool
	DeviceType string
}


func (s *SmartContract) CreateUser(ctx contractapi.TransactionContext, id string, name string, role string, condition map[string]string, usagelimit int, location [3]string, status bool) error{
		
	err := ctx.GetClientIdentity().AssertAttributeValue("abac.creator", "true")
	if err !=nil{
		return fmt.Errorf("submitting client not authorized to create user, does not have abac.creator role")
	}

	exists, err := s.AssetExists(ctx, id)
	if err != nil{
		return err
	}
	if exists{
		return fmt.Errorf("The user %s already exists, name: ", id, name)
	}

	// Create new user struct
	user := UserAttributes{
		ID:          id,
		Name:        name,
		Role:        role,
		Condition:   condition,
		UsageLimits: usagelimit,
		Location:    location,
		Status:      status,
	}

	userJSON, err := json.Marshal(user)
	if err != nil{
		return err
	}

	// Save user to ledger
	err = ctx.GetStub().PutState(id, userJSON)
	if err != nil {
		return fmt.Errorf("failed to store user %s: %v", id, err)
	}

	return nil

}

func (s *SmartContract) CreateDevice(ctx contractapi.TransactionContext, id string, location string, operationalStatus bool, deviceType string) error{

	err := ctx.GetClientIdentity().AssertAttributeValue("abac.creator", "true")
	if err !=nil{
		fmt.Errorf("submitting client not authorized to create device, does not have abac.creator role")
	}

	exists, err := s.AssetExists(ctx, id)
	if err != nil{
		return err
	}
	if exists{
		return fmt.Errorf("The user %s already exists, name: ", id)
	}

	// Create new user struct
	deviceInfo := DeviceAttributes{
		ID:          id,
		Location:    location,
		OperationalStatus: operationalStatus,
		DeviceType:  deviceType,
	}

	deviceJSON, err := json.Marshal(deviceInfo)
	if err != nil{
		return err
	}
	// Save user to ledger
	err = ctx.GetStub().PutState(id, deviceJSON)
	if err != nil {
		return fmt.Errorf("failed to store device %s: %v", id, err)
	}

	return nil
}

// AssetExists returns true when asset with given ID exists in world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {

	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return assetJSON != nil, nil
}


// GetSubmittingClientIdentity returns the name and issuer of the identity that
// invokes the smart contract. This function base64 decodes the identity string
// before returning the value to the client or smart contract.
func (s *SmartContract) GetSubmittingClientIdentity(ctx contractapi.TransactionContextInterface) (string, error) {

	b64ID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return "", fmt.Errorf("Failed to read clientID: %v", err)
	}
	decodeID, err := base64.StdEncoding.DecodeString(b64ID)
	if err != nil {
		return "", fmt.Errorf("failed to base64 decode clientID: %v", err)
	}
	return string(decodeID), nil
}



