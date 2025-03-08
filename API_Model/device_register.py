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
                "--id.name", "creator1",
                "--id.secret", "creator1pw",
                "--id.type", "client",
                "--id.affiliation", "org1",
                "--id.attrs", f"abac.location={location}:ecert,abac.creator=true:ecert,abac.status=true:ecert",
                "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
            ]

            enroll_device = [
                "fabric-ca-client", "enroll",
                "-u", "https://creator1:creator1pw@localhost:7054",
                "--caname", "ca-org1",
                "-M", f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp",
                "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
            ]
            
            # Register the device
            register_device = subprocess.run(register_device, cwd=network_directory, env=env, capture_output=True, check=True)

            # Check if registration was successful
            get_output, get_error = register_device.stdout

            if register_device.returncode != 0:
                return jsonify({"error": "Failed to register device"})
            

            # Enroll the device
            enroll_device = subprocess.run(enroll_device, cwd=network_directory, env=env, capture_output=True, check=True)

            # Check if enrollment was successful
            if enroll_device.returncode != 0:
                return jsonify({"error": "Failed to enroll device"})

            copy_config = [
                "cp",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/msp/config.yaml",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp/config.yaml"
            ]

            check = subprocess.run(copy_config, cwd=network_directory, env=env, check=True)

            if check.returncode != 0:
                return jsonify({"error": "Failed to copy config file"})

            # Check if directory exists
            if not os.path.exists(network_directory):
                return jsonify({"error": f"Directory does not exist: {network_directory}"})

            # Run command in that directory
            result = subprocess.run(register_device, shell=True, cwd=network_directory, check=True, capture_output=True, text=True)

            return jsonify({
                "message": f"Device registered successfully",
                "register_device": get_output
            })

        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Command failed with exit code {e.returncode}: {str(e)}"})
        except Exception as e:
            return jsonify({"error": str(e)})
        
    



