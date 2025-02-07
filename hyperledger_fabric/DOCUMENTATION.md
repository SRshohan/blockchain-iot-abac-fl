# Start with Fablo Installation

 Execute in the project root:

 ```sh
curl -Lf https://github.com/hyperledger-labs/fablo/releases/download/2.1.0/fablo.sh -o ./fablo && chmod +x ./fablo
 ```

## Getting started

To create a local Hyperledger Fabric network with Node.js chaincode and REST API client, install Fablo and execute:

```sh
./fablo init node rest
./fablo up
```

## Setup Example
    - node
    - chaincode


## Basic Usages

```sh
./fablo up fablo-config.json
```

### Sample Command
Generated fablo-config.json file uses single node solo/raft consensus and no TLS support:

```sh
./fablo init node dev
```

## Maintain Network (Down, Up, Reset, Recreate, Start)

### Up & Down
```sh
./fablo up fablo-config.json
./fablo down fablo-config.json
```

### Reset & Recreate
```sh
./fablo reset
./fablo recreate fablo-config.json
```

* `reset` -- down and up steps combined. Network state is lost, but the configuration is kept intact. Useful in cases when you want a fresh instance of network without any state.
* `recreate` -- prunes the network, generates new config files and ups the network. Useful when you edited `fablo-config` file and want to start newer network version in one command.    


## Managing Chaincodes

### Chaincode(s) install and check

```sh
./fablo chaincodes install
```

### Chaincode invoke

Invokes chaincode with specific parameters:

```sh
./fablo chaincode invoke <peers-domains-comma-separated> <channel-name> <chaincode-name> <command> [transient]
```

#### sample command
```sh
./fablo chaincode invoke "peer0.org1.example.com" "my-channel1" "chaincode1" '{"Args":["KVContract:put", "name", "Willy Wonka"]}'
```

## Explorer setup
 
 In `fablo-config.json` look for `organization` then in `tools` add 
 
 
 ```sh
 ...
 "tools": {"explorer": true}
 ...
 ```

## CouchDB
Go to the Docker look for the link in Docker make sure to add `\_utils`

Admin `peer0` and Password `peer0Password`



