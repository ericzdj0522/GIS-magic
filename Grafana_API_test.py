import requests
import json

url = "https://grafana.edge.na-prod-1-cluster.k8s.cs.swiftnav.com/api/datasources/proxy/uid/P5DCFC7561CCDE821/api/v1/query"

headers = {
    "Authorization": "Bearer glsa_nZpfjx66SQtPCZSA1yUSI7ipo7PfYI6z_0310c693",
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