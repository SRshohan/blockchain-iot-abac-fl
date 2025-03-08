import os
import subprocess

absp = os.path.abspath("../hyperledger_fabric/fabric-samples/test-network")

command = ["echo", "Hello World!"]
result = subprocess.run(command, cwd=absp, capture_output=True, check=True)

print(result.stdout)