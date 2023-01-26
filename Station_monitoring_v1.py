import os
import requests
import datetime
import time

# Routers endpoint
url_routers = 'https://www.cradlepointecm.com/api/v2/routers/'

# Routers alerts endpoint
url_routers_alerts = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router__in='


headers = {
    'X-CP-API-ID': os.environ['X_CP_API_ID'],
    'X-CP-API-KEY': os.environ['X_CP_API_KEY'],
    'X-ECM-API-ID': os.environ['X_ECM_API_ID'],
    'X-ECM-API-KEY': os.environ['X_ECM_API_KEY'],
    'Content-Type': 'application/json'
}


# Request DT stations device lists
def request_dt_list(url):
    device_list = []
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        for i in range(0, len(routers_resp['data'])):
            # Filter out DT station using group id
            if (routers_resp['data'][i]['group'] is not None):
                if ('205072' in routers_resp['data'][i]['group']):
                    device_list.append(routers_resp['data'][i]['id'])
        # Move to next group
        url = routers_resp['meta']['next']

    return device_list


# Request alert messages for devices
def request_routeralerts(url, router_id, time_start, time_end):
    print "API request start"
    url = url + router_id + '&created_at__lt=' + time_end + '&created_at__gt=' + time_start

    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        if 'data' in routers_resp.keys():
            for i in range(0, len(routers_resp['data'])):
                # print routers alerts message
                print '{0} : {1}, {2}, {3}'.format(routers_resp['data'][i]['router'], routers_resp['data'][i]['type'], routers_resp['data'][i]['created_at'], routers_resp['data'][i]['friendly_info'])

            # Move to next group
            url = routers_resp['meta']['next']

    print "API request finished"


# Request router list for all devices
def request_routerlist(url):
    device_list = []
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        for i in range(0, len(routers_resp['data'])):
            device_list.append(routers_resp['data'][i]['id'])

        # Move to next group
        url = routers_resp['meta']['next']

    return device_list


if __name__ == '__main__':
    # Request first 10 devices id lists, API call has 100 devices limits
    router_list = request_routerlist(url_routers)
    router_group = ''
    for i in range(0, 10):
        if i == 0:
            router_group = router_group + router_list[0]
        else:
            router_group = router_group + ',' + router_list[i]

    # Record API call start time
    time_tracker = []

    while True:
        # Set up datetime range for routers alerts
        current_time = datetime.datetime.now()
        print current_time
        if len(time_tracker) == 0:
            start_time = current_time - datetime.timedelta(seconds=60)
        else:
            start_time = time_tracker[0]
        print start_time

        current_time_str = current_time.strftime("%m-%d-%YT%H:%M:%S")
        start_time_str = start_time.strftime("%m-%d-%YT%H:%M:%S")

        # Manually assign a datetime range, since 60 seconds resolution might be too frequent to alert messages
        # current_time_str = '2020-12-30'
        # start_time_str = '2020-12-15'

        # API request for alert message
        request_routeralerts(url_routers_alerts, router_group, start_time_str, current_time_str)
        time_tracker[:] = []
        time_tracker.append(current_time)

        # Calculation function execution time and set up sleep time for API call
        finish_time = datetime.datetime.now()
        API_call_time = finish_time - current_time

        time.sleep(60 - API_call_time.total_seconds())


