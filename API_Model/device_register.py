from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess


class DeviceRegister(Resource):
    def post(self):
        try:
            data = request.get_json()
            location = data.get("location")
            device_id = data.get("device_id")

            if not location or not device_id:
                return jsonify({"error": "Missing location or device_id"}), 400

            network_directory = "hyperledger_fabric/fabric-samples/test-network"

            # Run commands inside the test-network directory
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

            # Enroll the device
            enroll_device = [
                "fabric-ca-client", "enroll",
                "-u", "https://creator3:creator1pw@localhost:7054",
                "--caname", "ca-org1",
                "-M", f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp",
                "--tls.certfiles", f"{network_directory}/organizations/fabric-ca/org1/tls-cert.pem"
            ]

            subprocess.run(enroll_device, cwd=network_directory, env=env, check=True)

            # Copy the certificate
            copy_cert = [
                "cp",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/msp/config.yaml",
                f"{network_directory}/organizations/peerOrganizations/org1.example.com/users/creator3@org1.example.com/msp/config.yaml"
            ]

            subprocess.run(copy_cert, cwd=network_directory, check=True)

            return jsonify({"message": "Device registered successfully"})

        except subprocess.CalledProcessError as e:
            return jsonify({"error": "Hyperledger Fabric command failed", "details": str(e)})
        except Exception as e:
            return jsonify({"error": str(e)})
