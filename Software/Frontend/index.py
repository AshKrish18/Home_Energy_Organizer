import requests

BASE_URL = "http://127.0.0.1:8000"

devices = ["fridge", "washer", "ac", "lights"]

for device in devices:
    r = requests.get(f"{BASE_URL}/readings/{device}?limit=1")
    if r.status_code == 200:
        data = r.json()
        print(f"{device}: {data['readings']}")
    else:
        print(f"Failed to fetch {device}: {r.status_code}")