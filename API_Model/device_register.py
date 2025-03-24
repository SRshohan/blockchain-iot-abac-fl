from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess
import os

class DeviceRegister(Resource):
    def post(self):
        data = request.get_json()
        location = data.get("location")
        device_id = data.get("device_id")

        if not location or not device_id:
            return jsonify({"error": "Missing location or device_id"})

        # Convert to absolute path
        network_directory = os.path.abspath("../hyperledger_fabric/fabric-samples/test-network")

        if not os.path.exists(network_directory):
            return jsonify({"error": f"Directory does not exist: {network_directory}"})

        # Set up environment variables
        env = os.environ.copy()
        env.update({
            "PATH": f"{network_directory}/../bin:{network_directory}:{env['PATH']}",
            "FABRIC_CFG_PATH": f"{network_directory}/../config/",
            "FABRIC_CA_CLIENT_HOME": f"{network_directory}/organizations/peerOrganizations/org1.example.com/"
        })

        # Define paths
        source_config_path = f"{network_directory}/organizations/peerOrganizations/org1.example.com/msp/config.yaml"
        target_directory = f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp"
        target_config_path = f"{target_directory}/config.yaml"

        # Ensure the target directory exists
        os.makedirs(target_directory, exist_ok=True)

        # Ensure source config exists
        if not os.path.exists(source_config_path):
            return jsonify({"error": f"Source config.yaml does not exist: {source_config_path}"})

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
            "-M", target_directory,
            "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
        ]

        copy_config = ["cp", source_config_path, target_config_path]

        # Execute Register Command
        register_result = subprocess.run(register_device, cwd=network_directory, env=env, capture_output=True, text=True)

        if register_result.returncode != 0:
            return jsonify({"error": f"Failed to register device: {register_result.stderr}"})

        # Execute Enroll Command
        enroll_result = subprocess.run(enroll_device, cwd=network_directory, env=env, capture_output=True, text=True)

        if enroll_result.returncode != 0:
            return jsonify({"error": f"Failed to enroll device: {enroll_result.stderr}"})

        # Copy Config File
        copy_result = subprocess.run(copy_config, cwd=network_directory, env=env, capture_output=True, text=True)

        if copy_result.returncode != 0:
            return jsonify({"error": f"Failed to copy config file: {copy_result.stderr}"})

        return jsonify({"message": "Device registered successfully"})




        
    



