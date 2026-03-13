import requests
import json

url = "test"

headers = {
    "Authorization": "test",
    "Content-Type": "application/json"
}

params = {
    "query": 'max by (station)(orion_ntrip_client_bytes_sum{cluster=~"(na|na2)"})'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
metrics_dict = {
    item['metric']['station']: float(item['value'][1])
    for item in data['data']['result']
}
print(response.status_code)
print(metrics_dict)