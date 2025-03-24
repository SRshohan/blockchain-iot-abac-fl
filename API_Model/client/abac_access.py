import requests

def abac(client_id, location, device_id):
    response = requests.post(
        "http://localhost:8081/device/access", data={"location": location, "device_id": device_id}
    )

    return response

    

    

