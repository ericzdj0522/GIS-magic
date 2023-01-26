import json
import requests
import datetime

# API end point Router
url = 'https://www.cradlepointecm.com/api/v2/routers/?group='

# Device metrics endpoint
url2 = 'https://www.cradlepointecm.com/api/v2/net_device_metrics/'

# Currently Router Alerts not working
url3 = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router__in='

# Device health status
url4 = 'https://www.cradlepointecm.com/api/v2/net_device_health/'

# General alerts
url7 = 'https://www.cradlepointecm.com/api/v2/alerts/?router=844293'

#Create router alerts
url8 = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router=844293'


url_routers_alerts = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router__in='
headers = {
    'X-CP-API-ID': '858ea9ec',
    'X-CP-API-KEY': 'f7b770329195a35ecbd5f40a2e1c30c9',
    'X-ECM-API-ID': '3c5eb038-2c22-4c13-a365-91e5eb44971a',
    'X-ECM-API-KEY': 'b85a7b9719f25e84e8cf5cec4379892ea79bddb4',
    'Content-Type': 'application/json'
}


def requestrouter(url, router_group, time_start, time_end):
    url = url + router_group + '&created_at__lt=' + time_end + '&created_at__gt=' + time_start
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        print(routers_resp)
        for i in range (0, len(routers_resp['data'])):
            #print routers_resp['data'][i]
            print('{0} : {1}, {2}, {3}'.format(routers_resp['data'][i]['router'], routers_resp['data'][i]['type'], routers_resp['data'][i]['created_at'], routers_resp['data'][i]['friendly_info']))

         # Move to next group
        url = routers_resp['meta']['next']





if __name__ == '__main__':

    requestrouter(url_routers_alerts, '1435902', '2022-06-26', '2022-06-27')