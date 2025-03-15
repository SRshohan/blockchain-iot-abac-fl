from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess

class DeviceAccess(Resource):
    def post(self):
        try:
            data = request.get_json()
            location = data.get("location")
            device_id = data.get("device_id")

            if not location or not device_id:
                return jsonify({"error": "Missing location or device_id"})

            network_directory = "../hyperledger_fabric/fabric-samples/test-network"
            
            # Setup variables for device identity
            identity_variables = {
                "PATH": f"{network_directory}/../bin:{network_directory}:${{PATH}}",
                "FABRIC_CFG_PATH": f"{network_directory}/../config/",
                "FABRIC_CA_CLIENT_HOME": f"{network_directory}/organizations/peerOrganizations/org1.example.com/",
                "CORE_PEER_TLS_ENABLED" : "true",
                "CORE_PEER_LOCALMSPID" : "Org1MSP",
                "CORE_PEER_MSPCONFIGPATH" : f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp",
                "CORE_PEER_TLS_ROOTCERT_FILE" : f"{network_directory}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
                "CORE_PEER_ADDRESS" : "localhost:7051",
                "TARGET_TLS_OPTIONS" : f"""(-o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "{network_directory}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --peerAddresses localhost:7051 --tlsRootCertFiles "{network_directory}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "{network_directory}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt")"""
            }
            
            #Access device
            access_device = [
                "peer", "chaincode", "invoke", "mychannel", "abac", '{"function":"AccessDevice", "Args":[f"{device_id}"]}'
            ]
            
            subprocess.run(access_device, cwd=network_directory, env=identity_variables, check=True)

            return jsonify({"message": "Device registered successfully"})
        except subprocess.CalledProcessError as e:
            return jsonify({"error": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})