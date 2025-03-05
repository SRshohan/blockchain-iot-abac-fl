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

            # Run commands inside the test-network director 
            env = {
                "PATH": f"{network_directory}/../bin:{network_directory}:${{PATH}}",
                "FABRIC_CFG_PATH": f"{network_directory}/../config/",
                "FABRIC_CA_CLIENT_HOME": f"{network_directory}/organizations/peerOrganizations/org1.example.com/"
            }

            # Register the device
            register_device = [
                "fabric-ca-client", "register",
                "--id.name", "creator3",
                "--id.secret", "creator1pw",
                "--id.type", "client",
                "--id.affiliation", "org1",
                "--id.attrs", f"abac.location={location}:ecert,abac.creator=true:ecert,abac.status=true:ecert",
                "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
            ]
            
            subprocess.run(register_device, cwd=network_directory, env=env, check=True)

            return jsonify({"message": "Device registered successfully"})
        except subprocess.CalledProcessError as e:
            return jsonify({"error": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})