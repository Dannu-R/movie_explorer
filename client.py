import requests
import json

item = "banana"

response = requests.get("http://127.0.0.1:8000/tasks")
data = response.json()
print(data)
