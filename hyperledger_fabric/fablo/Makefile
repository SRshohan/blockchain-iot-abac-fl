# Makefile for Hyperledger Fabric Chaincode Operations
# -----------------------------------------------------

# Environment Variables
# ---------------------
CHANNEL ?= my-channel1
CC_NAME ?= chaincode1
CC_VERSION ?= 1.0
PEER_ADDRESS ?= peer0.org1.example.com:7041
CC_SEQUENCE ?= 1

# Default Target
# --------------
help:
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  network-up  - Start the Fabric network"
	@echo "  network-down- Stop the Fabric network"
	@echo "  install     - Install chaincode"
	@echo "  approve     - Approve chaincode"
	@echo "  commit      - Commit chaincode"
	@echo "  invoke      - Invoke chaincode function (ARGS=required)"
	@echo "  query       - Query chaincode function (ARGS=required)"
	@echo "  clean       - Clean generated files"

# Network Management
# ------------------
network-up:
	@echo "Starting Fabric network..."
	./fablo up fablo-config.json

network-down:
	@echo "Stopping Fabric network..."
	./fablo down

# Chaincode Lifecycle
# -------------------
install:
	@echo "Installing chaincode..."
	./fablo chaincode install $(CC_NAME) ./chaincode-kv-node

approve:
	@echo "Approving chaincode..."
	./fablo chaincode approve $(CC_NAME) $(CC_VERSION)

commit:
	@echo "Committing chaincode..."
	./fablo chaincode commit $(CC_NAME) $(CC_VERSION)

# Chaincode Operations
# --------------------
invoke:
	./fablo chaincode invoke "peer0.org1.example.com" "my-channel1" "chaincode1" \
		'{"function":"put","Args":["doc1","{\"owner\":\"alice\",\"timestamp\":\"2023-08-20T12:34:56Z\",\"data\":\"sample\"}"]}'

query:
	@echo "Querying chaincode function..."
	docker exec $(PEER_ADDRESS) peer chaincode query \
		-C $(CHANNEL) \
		-n $(CC_NAME) \
		-c '$(ARGS)'

# Cleanup
# -------
clean:
	@echo "Cleaning network..."
	./fablo prune
	rm -rf /tmp/hfc*

# Non-file Targets
# ----------------
.PHONY: help network-up network-down install approve commit invoke query clean