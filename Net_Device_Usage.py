import json
import requests

API_OBJ_REQUEST_SIZE = 100
API_OBJ_RESPONSE_SIZE = 500

START_DATE = '2020-9-19'
END_DATE = '2020-9-25'


# Chunk lists into blocks
def chunker(seq, size):
    return (seq[pos: pos + size] for pos in range(0, len(seq), size))


# Get the next url, at completion return None
def next_url(resp):
    if resp['meta']['next']:
        url = resp['meta']['next']
    else:
        url = None

    return url


# API Keys
headers = {
    'X-CP-API-ID': '858ea9ec',
    'X-CP-API-KEY': 'f7b770329195a35ecbd5f40a2e1c30c9',
    'X-ECM-API-ID': '8e1a477a-e263-43fb-a5e4-dbf66c988d4d',
    'X-ECM-API-KEY': '02dcd97653ccb5cc81d4f3ebf2cb391a631a45ae',
    'Content-Type': 'application/json'
}

# Get net_devices
net_device_ids = set()
url = 'https://www.cradlepointecm.com/api/v2/net_devices/?limit={}'. \
    format(API_OBJ_RESPONSE_SIZE)
while url:
    req = requests.get(url, headers=headers)
    resp = req.json()
    for net_device in resp['data']:
        net_device_ids.add(int(net_device['id']))
    url = next_url(resp)

print (net_device_ids)

# Get usage samples
print ('bytes_in, bytes_out, created_at, created_at_timeuuid'
       'net_device, period, uptime')
for net_devices in chunker(sorted(net_device_ids), API_OBJ_REQUEST_SIZE):
    url = 'https://www.cradlepointecm.com/api/v2/net_device_usage_samples/' \
          '?limit={}'.format(API_OBJ_RESPONSE_SIZE)
    url += '&net_device__in={}'.format(','.join(map(str, net_devices)))
    url += '&created_at__gt={}&created_at__lt={}'.format(START_DATE, END_DATE)
    url += '&order_by=created_at_timeuuid'
    #print url

    while url:
        req = requests.get(url, headers=headers)
        resp = req.json()
        #print resp
        if (len(resp['data']) > 0):
            for net_device in resp['data']:
                print('{},{},{},{}'.format(
                    net_device['bytes_in'],
                    net_device['bytes_out'],
                    net_device['created_at'],
                    net_device['created_at_timeuuid'],
                    #net_device['net_device'],
                    #net_device['period'],
                    #net_device['uptime']
                    ))
        url = next_url(resp)




# Get signal samples
'''
print('created_at,created_at_timeuuid,ecio,net_device,rssi,'
      'signal_percent,sinr,uptime')
for net_devices in chunker(sorted(net_device_ids), API_OBJ_REQUEST_SIZE):
    url = 'https://www.cradlepointecm.com/api/v2/net_device_signal_samples/' \
        '?limit={}'.format(API_OBJ_RESPONSE_SIZE)
    url += '&net_device__in={}'.format(','.join(map(str, net_devices)))
    url += '&created_at__gt={}&created_at__lt={}'.format(START_DATE, END_DATE)
    url += '&order_by=created_at_timeuuid'
    print url

    while url:
        req = requests.get(url, headers=headers)
        resp = req.json()
        print resp
        if (len(resp['data']) > 0):
            for net_device in resp['data']:
                print('{},{},{},{},{},{},{},{}'.format(
                    net_device['created_at'],
                    net_device['created_at_timeuuid'],
                    net_device['ecio'],
                    net_device['net_device'],
                    net_device['rssi'],
                    net_device['signal_percent'],
                    net_device['sinr'],
                    net_device['uptime']))
        url = next_url(resp)
'''