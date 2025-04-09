from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess
import os

def modelTraining(client_id, location, status):
    # Get absolute paths
    current_dir = os.path.abspath(os.path.dirname(__file__))
    network_directory = os.path.abspath(os.path.join(current_dir, "../hyperledger_fabric/fabric-samples/test-network"))
    bin_directory = os.path.abspath(os.path.join(network_directory, "../bin"))
    
    # Get the current PATH and add our directories
    current_path = os.environ.get('PATH', '')
    new_path = f"{bin_directory}:{network_directory}:{current_path}"
    
    # Setup variables for device identity
    identity_variables = os.environ.copy()  # Start with current environment
    identity_variables.update({
        "PATH": new_path,
        "FABRIC_CFG_PATH": os.path.abspath(os.path.join(network_directory, "../config/")),
        "FABRIC_CA_CLIENT_HOME": os.path.abspath(os.path.join(network_directory, "organizations/peerOrganizations/org1.example.com/")),
        "CORE_PEER_TLS_ENABLED": "true",
        "CORE_PEER_LOCALMSPID": "Org1MSP",
        "CORE_PEER_MSPCONFIGPATH": os.path.abspath(os.path.join(network_directory, f"organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp")),
        "CORE_PEER_TLS_ROOTCERT_FILE": os.path.abspath(os.path.join(network_directory, "organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt")),
        "CORE_PEER_ADDRESS": "localhost:7051"
    })
    
    # Check if peer binary exists
    peer_path = os.path.join(bin_directory, "peer")
    if not os.path.exists(peer_path):
        return {"success": False, "error": f"Peer binary not found at {peer_path}"}
    
    # Set absolute path to peer binary
    peer_command = peer_path
    
    # JSON arguments
    json_args = f'{{"function":"CallModelTrainingAbac","Args":["{client_id}","{location}","{status}"]}}'
    
    # Construct the command
    access_device = [
        peer_command,
        "chaincode", "invoke", 
        "-C", "mychannel", 
        "-n", "abac", 
        "-c", json_args,
        "-o", "localhost:7050", 
        "--ordererTLSHostnameOverride", "orderer.example.com",
        "--tls",
        "--cafile", os.path.join(network_directory, "organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"),
        "--peerAddresses", "localhost:7051",
        "--tlsRootCertFiles", os.path.join(network_directory, "organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"),
        "--peerAddresses", "localhost:9051",
        "--tlsRootCertFiles", os.path.join(network_directory, "organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt")
    ]

    try:
        # Add debug logging
        # print(f"Executing: {' '.join(access_device)}")
        # print(f"Working directory: {network_directory}")
        # print(f"PATH: {identity_variables['PATH']}")
        
        result = subprocess.run(access_device, cwd=network_directory, env=identity_variables, 
                             capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        return {"success": True, "output": result.stdout}
    except Exception as e:
        return {"success": False, "error": str(e)}


        

# class Train_model(Resource):
#     def post(self):
#         try:
#             data = request.get_json()
#             ip = data.get("ip")

#             if not ip:
#                 return jsonify({"error": "Missing ip"})
            
#             if ip == "192.168.1.217":
#                 return 

#             network_directory = "../hyperledger_fabric/fabric-samples/test-network"
            
#             # Setup variables for device identity
#             identity_variables = {
#                 "PATH": f"{network_directory}/../bin:{network_directory}:${{PATH}}",
#                 "FABRIC_CFG_PATH": f"{network_directory}/../config/",
#                 "FABRIC_CA_CLIENT_HOME": f"{network_directory}/organizations/peerOrganizations/org1.example.com/",
#                 "CORE_PEER_TLS_ENABLED" : "true",
#                 "CORE_PEER_LOCALMSPID" : "Org1MSP",
#                 "CORE_PEER_MSPCONFIGPATH" : f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/{id}@org1.example.com/msp",
#                 "CORE_PEER_TLS_ROOTCERT_FILE" : f"{network_directory}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
#                 "CORE_PEER_ADDRESS" : "localhost:7051",
#                 "TARGET_TLS_OPTIONS" : f"""(-o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "{network_directory}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --peerAddresses localhost:7051 --tlsRootCertFiles "{network_directory}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "{network_directory}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt")"""
#             }

#         except Exception as e:
#             pass

import requests

url = "https://7abc-2600-4041-5592-500-cf8b-dcef-644-172f.ngrok-free.app/ModelTraining"

response = requests.get(url).json()



if __name__ == "__main__":
    print(modelTraining("pi1", response["location"], response["status"]))