from device_register import DeviceRegister
from device_access import DeviceAccess
from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS
from user_access import UserAccess

class DeviceOs(Resource):
    def get(self):
        return {"os": "Linux"}


app = Flask(__name__)
CORS(app)
api = Api(app)


api.add_resource(DeviceRegister, "/device/register")
api.add_resource(DeviceAccess, "/device/access")
api.add_resource(DeviceOs, "/device/os")
api.add_resource(UserAccess, "/user/access")

if __name__ == "__main__":
    app.run(debug=True)