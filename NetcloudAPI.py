import json
import requests
import csv
import datetime

# API end point
url = 'https://www.cradlepointecm.com/api/v2/routers/'

# Device metrics endpoint
url2 = 'https://www.cradlepointecm.com/api/v2/net_device_metrics/'

# Currently Router Alerts not working
url3 = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router='

# Device health status
url4 = 'https://www.cradlepointecm.com/api/v2/net_device_health/'

url5 = 'https://www.cradlepointecm.com/api/v2/router_state_samples/?router='

url6 = 'https://www.cradlepointecm.com/api/v2/router_stream_usage_samples/'

url7 = 'https://www.cradlepointecm.com/api/v2/alerts/?router=844293'
url8 = 'https://www.cradlepointecm.com/api/v2/router_alerts/?router=844293'

headers = {
    'X-CP-API-ID': '858ea9ec',
    'X-CP-API-KEY': 'f7b770329195a35ecbd5f40a2e1c30c9',
    'X-ECM-API-ID': '8e1a477a-e263-43fb-a5e4-dbf66c988d4d',
    'X-ECM-API-KEY': '02dcd97653ccb5cc81d4f3ebf2cb391a631a45ae',
    'Content-Type': 'application/json'
}


#Export station status for QGIS
def cradlepointrequest(url):
    req = requests.get(url, headers=headers)
    routers_resp = req.json()
    csvheader = ["custom1", "state"]
    csv_file = '/Users/dj/Documents/QGIS/CSV/China/CONUS_status.csv'

    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csvheader)
        writer.writeheader()
        while url:
            req = requests.get(url, headers=headers)
            routers_resp = req.json()
            for i in range (0, len(routers_resp['data'])):
                if(routers_resp['data'][i]['custom1'] is not None):
                    if('USA' in routers_resp['data'][i]['custom1']):
                        print(routers_resp['data'][i])
                        tempdict = routers_resp['data'][i]
                        newdict = {key: value for key, value in tempdict.items() if key=="custom1" or key=="state"}
                        newdict['custom1']= newdict['custom1'][0:4]
                        writer.writerow(newdict)
                        '''
                        Id = routers_resp['data'][i]['custom1']
                        State = routers_resp['data'][i]['state']
                        print '{0} : {1}'.format(Id, State)
                        requestRouteralert(url3, routers_resp['data'][i]['id'])
                        print '\n'
                        '''
            '''
            for i in range(0, 20, 1):
                print routers_resp['data'][i]['id']
            '''
            # Get URL for next set of resources
            url = routers_resp['meta']['next']

# Pull out each router status
def requestRouter(url):
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        for i in range (0, len(routers_resp['data'])):
            print routers_resp['data'][i]

         # Move to next group
        url = routers_resp['meta']['next']

# Measure router connectivity
def requestRouterlog(url, routerid):
    url = url + routerid
    print url
    req = requests.get(url, headers=headers)
    routers_resp = req.json()
    for i in range (0, len(routers_resp['data'])):
        print routers_resp['data'][i]

#Testing on router alert message
def requestRouteralert(url, routerid):
    url = url + routerid
    print url
    req = requests.get(url, headers=headers)
    routers_resp = req.json()
    '''
    #Double check alert time difference to filter out UPS check
    alert1_time = datetime.datetime.strptime(routers_resp['data'][0]['detected_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
    alert2_time = datetime.datetime.strptime(routers_resp['data'][1]['detected_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
    difference = alert1_time - alert2_time
    print difference.total_seconds()
    '''
    if len(routers_resp['data']) != 0:
        alerttype = str(routers_resp['data'][0]['type'])
        alertinfo = str(routers_resp['data'][0]['friendly_info'])

        alertlist = routers_resp['data']
        #Time difference between first and second alert, current time and first alert to filter out UPS check
        timediff1, timediff2 = timediff_alert(alertlist)
        print timediff1, timediff2
        power_alert(alerttype, alertinfo, timediff1, timediff2)

    else:
        print '{0} : {1}'.format(routerid, 'No alert for this device')

    #loop through all history alerts
    '''
    for i in range (0, len(routers_resp['data'])):
        alerttype = routers_resp['data'][i]['type']
        alertinfo = routers_resp['data'][i]['friendly_info']
        power_alert(alerttype, alertinfo, timediff1, timediff2)
        #print '{0} : {1}'.format(alerttype, alertinfo)
    '''
#Calculate time difference between first and second alert, and time difference between current time and first alert
def timediff_alert(alertlist):
    if len(alertlist)>1:
        alert1_time = datetime.datetime.strptime(alertlist[0]['detected_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
        alert2_time = datetime.datetime.strptime(alertlist[1]['detected_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
        current_time = datetime.datetime.now()

        difference = alert1_time - alert2_time
        difference2 = current_time - alert1_time
        # seconds difference between alert 1 and alert 2
        timediff1 = difference.total_seconds()
        # seconds difference between current time and alert 1
        timediff2 = difference2.total_seconds()
        return timediff1, timediff2
    else:
        alert1_time = datetime.datetime.strptime(alertlist[0]['detected_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
        current_time = datetime.datetime.now()
        difference2 = current_time - alert1_time
        # seconds difference between current time and alert 1
        timediff2 = difference2.total_seconds()
        return 0, timediff2

#Generate alert message based on cradlepoint alert information
def power_alert(alerttype, alertinfo, timediff1, timediff2):
    if alerttype == 'gpio_state_change':
        if 'Power Source is Grid Power' in alertinfo:
            if timediff1 < 10:
                print "Just UPS self-check"
            else:
                print "Power is back to Grid Power"
        elif 'Power Source is Backup Battery' in alertinfo:
            if timediff2 > 10:
                print "Power is switched to Battery, might be a UPS self-check"
            else:
                print "Just UPS self-check"
        elif 'Battery State is Exhausted' in alertinfo:
            print "Battery need be charged"
        elif 'Battery Health is Good Condition' in alertinfo:
            print 'Power is back to Grid Power'

    # Connection status alert
    elif alerttype == 'connection_state':
        if 'offline' in alertinfo:
            print "Power is going down"
        elif 'online' in alertinfo:
            print "Power is back to normal"

    # Other type of alert
    else:
        print alertinfo


#Generate all router device list on netcloud
def requestDevicelist(url):
    devicelist = []
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        for i in range (0, len(routers_resp['data'])):
            print routers_resp['data'][i]['id']
            devicelist.append(routers_resp['data'][i]['id'])

         # Move to next group
        url = routers_resp['meta']['next']
    return devicelist

#Request power information for specific router device
def requestPowerinfo(url, routerid):
    url = url + routerid
    req = requests.get(url, headers=headers)
    routers_resp = req.json()
    if len(routers_resp['data']) != 0:
        powerinfo = routers_resp['data'][0]['friendly_info']
        print '{0} : {1}'.format(routerid, powerinfo)
    else:
        print '{0} : {1}'.format(routerid, 'No alert for this device')

#Request connection information for all router
def requestConnectioninfo(url):
    while url:
        req = requests.get(url, headers=headers)
        routers_resp = req.json()
        for i in range(0, len(routers_resp['data'])):
            Id = routers_resp['data'][i]['id']
            State = routers_resp['data'][i]['state']
            print '{0} : {1}'.format(Id, State)

        # Move to next group
        url = routers_resp['meta']['next']

 # Writing JSON output for data
def jsonexporter():
    with open('/Users/dj/Documents/QGIS/GeoJson/Test.json', 'w') as f:
        while url:
            req = requests.get(url, headers=headers)
            routers_resp = req.json()
            print routers_resp
            #Check record
            json.dump(routers_resp, f, indent=2)
            # Get URL for next set of resources
            url = routers_resp['meta']['next']


if __name__ == '__main__':
    # cradlepointrequest(url)
    #requestRouter(url7)


    devicelist = requestDevicelist(url)
    print len(devicelist)
    #Check every single device power status
    for i in range(0, len(devicelist)):
        if devicelist[i] != '1267235':
            requestRouteralert(url3, devicelist[i])

    #requestConnectioninfo(url)



    #requestPowerinfo(url3, '844293')

    # requestRouterlog(url5, '1435900')

    #requestRouteralert(url3, '1267235')




