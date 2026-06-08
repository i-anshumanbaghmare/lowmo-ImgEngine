import requests
import json
import re

url = "https://civitai.com/api/download/models/2499141"
match = re.search(r"models/(\d+)", url)
if match:
    version_id = match.group(1)
    api_url = f"https://civitai.com/api/v1/model-versions/{version_id}"
    resp = requests.get(api_url)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print("Files:")
    for f in data.get("files", []):
        print(f["name"], f.get("type"))
    
    print("Model ID:", data.get("modelId"))
    
    model_resp = requests.get(f"https://civitai.com/api/v1/models/{data.get('modelId')}")
    model_data = model_resp.json()
    print("Model Type:", model_data.get("type"))
