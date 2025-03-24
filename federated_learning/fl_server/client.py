import tensorflow as tf
import flwr as fl
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Define and compile the model
model = tf.keras.applications.MobileNetV2(
    (32, 32, 3),
    classes=10,
    weights=None
)
model.compile(
    'adam',
    "sparse_categorical_crossentropy",
    metrics=['accuracy']
)

# Load dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

class CifarClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return model.get_weights()
    
    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=5, batch_size=8)
        return model.get_weights(), len(x_train), {}
    
    def evaluate(self, parameters, config):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": accuracy}

fl.client.start_numpy_client(
    server_address="192.168.1.14:8080",
    client=CifarClient()
)