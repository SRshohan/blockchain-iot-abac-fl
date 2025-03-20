## Federated Learning Setup

### Install Flower
```bash
pip install flower
```

### Create Federated Learning Project
```bash
flwr new
```

### Start Flower Server
```bash
cd <project_name>
pip install -e .
flwr run .
```


### Flower Architecture
!(link)[https://flower.ai/docs/framework/explanation-flower-architecture.html]


## Embedded federated learning

### Create Federated Learning Project example
```bash
git clone --depth=1 https://github.com/adap/flower.git \
          && mv flower/examples/embedded-devices . \
          && rm -rf flower && cd embedded-devices
```

### Install dependencies
```bash
pip install -e .
```

### Make sure embedded device has some data
Partition the Fashion-MNIST dataset into two partitions
```bash
python generate_dataset.py --num-supernodes=2
```

### Copy one partition to a device
Run this command from the home terminal of Mac/Linux and find out the IP address of the embedded device 
```bash
scp -r datasets/fashionmnist_part_1 sr@192.168.1.249:/home/sr/Desktop/fl_sys
```

### Run the superlink server
```bash
flower-superlink --insecure
```

### After activating your environment
```bash
pip install -U flwr
pip install torch torchvision datasets
```
### Severe the SuperLink startup
```bash
flower-superlink --insecure
```


### Run the client
Repeat for each embedded device (adjust SuperLink IP and dataset-path)
```bash
flower-supernode --insecure --superlink="192.168.1.14:9092" \
                 --node-config="dataset-path='path/to/fashionmnist_part_1'"
```

### Run the flower app
```bash
flwr run . embedded-federation
```


### need a try tensorflow federated