from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import subprocess
import os
import requests

url = "https://7abc-2600-4041-5592-500-cf8b-dcef-644-172f.ngrok-free.app/ModelTraining"

response = requests.get(url)
print

print(response.json())

