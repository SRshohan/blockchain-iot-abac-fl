from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess
import os


class DeviceRegister(Resource):
    def post(self):
        try:
            data = request.get_json()
            location = data.get("location")
            device_id = data.get("device_id")

            if not location or not device_id:
                return jsonify({"error": "Missing location or device_id"})

            # Convert to absolute path
            network_directory = os.path.abspath("../hyperledger_fabric/fabric-samples/test-network")

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

            enroll_device = [
                "fabric-ca-client", "enroll",
                "-u", "https://creator3:creator1pw@localhost:7054",
                "--caname", "ca-org1",
                "-M", f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp",
                "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
            ]
            
            subprocess.run(register_device, cwd=network_directory, env=env, check=True)
            subprocess.run(enroll_device, cwd=network_directory, env=env, check=True)

            copy_config = [
                "cp",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/msp/config.yaml",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp/config.yaml"
            ]

            subprocess.run(copy_config, cwd=network_directory, env=env, check=True)

            # Check if directory exists
            if not os.path.exists(network_directory):
                return jsonify({"error": f"Directory does not exist: {network_directory}"})

            # Run command in that directory
            result = subprocess.run(register_device, shell=True, cwd=network_directory, check=True, capture_output=True, text=True)

            return jsonify({
                "message": f"Device registered successfully",
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            })

        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Hyperledger Fabric command failed", "details": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})



