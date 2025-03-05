from device_register import DeviceRegister
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS

class DeviceOs(Resource):
    def get(self):
        return {"os": "Linux"}


app = Flask(__name__)
CORS(app)
api = Api(app)


api.add_resource(DeviceRegister, "/device/register")
api.add_resource(DeviceOs, "/device/os")

if __name__ == "__main__":
    app.run(debug=True)