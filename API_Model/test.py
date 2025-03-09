import os
import subprocess

absp = os.path.abspath("../hyperledger_fabric/fabric-samples/test-network")

command = ["echo", "Hello World"]
result = subprocess.run(command, capture_output=True)

print(result.stdout)