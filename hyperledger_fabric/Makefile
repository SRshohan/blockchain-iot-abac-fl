destroy:
	mkdir fablo && \
	cd fablo && \
	curl -Lf https://github.com/hyperledger-labs/fablo/releases/download/2.1.0/fablo.sh -o ./fablo && chmod +x ./fablo && \
	./fablo init node 


chaincode-deploy:
	cd fablo && \
	./fablo chaincode invoke "peer0.org1.example.com" "my-channel1" "chaincode1" \
    '{"Args":["KVContract:put", "name", "Admin", "Home 1", "Test Data"]}'