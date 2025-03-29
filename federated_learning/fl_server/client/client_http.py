from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
import time

# Client ID - unique for each device
CLIENT_ID = input("Enter client ID: ")
location = input("Enter location: ")
timezone = time.time()

# Function to get client information
def client_info():
    return{
        "client_id": CLIENT_ID,
        "location": location,
        "timezone": timezone,
        "status"  : "active"
    }

class sendData(Resource):
    def post(self, data):
        print(data)
        return jsonify(data)
app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(sendData, '/sendData')

app.run(host='0.0.0.0', port=5000)
    
