import requests
import json
import time
from requests.auth import HTTPBasicAuth
from prometheus_client import start_http_server, Gauge

# Define rest api requests
def rest_api_request(apiendpoint):
    # Define the URL of the API endpoint
    url = apiendpoint

    # Define any parameters or headers required by the API
    username = "ericzdj"
    password = "zdj19920522"

    # Send a GET request
    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content
        print(response.json())
        return response.json()
    else:
        # Print the error message
        print("Error:", response.status_code, response.text)


# Simulate api request for certain period of time
if __name__ == '__main__':
    #Test API endpoint, sim station status, rerun controlpoints analysis, and export metrics periodically
    cp_analysis = "http://127.0.0.1:8000/geo_api/cpmonthlystats/"
    cp_stats = "http://127.0.0.1:8000/geo_api/cpstats"
   #cp_test = "http://127.0.0.1:8000/geo_api/stationsim/"

    # define control points metrics to monitor
    level1_count_g = Gauge('level1_count_metric', 'metric for level 1 control points count')
    level2_count_g = Gauge('level2_count_metric', 'metric for level 2 control points count')
    level3_count_g = Gauge('level3_count_metric', 'metric for level 3 control points count')

    level1_pc_g = Gauge('level1_percent_metric', 'metric for level 1 control points percentage')
    level2_pc_g = Gauge('level2_percent_metric', 'metric for level 2 control points percentage')
    level3_pc_g = Gauge('level3_percent_metric', 'metric for level 3 control points percentage')

    level1_time_g = Gauge('level1_time_metric', 'metric for level 1 control point accumulated time')
    level2_time_g = Gauge('level2_time_metric', 'metric for level 2 control point accumulated time')
    level3_time_g = Gauge('level3_time_metric', 'metric for level 3 control point accumulated time')




    start_http_server(8001)


    while True:
        # Geo_api request, first to rerun control points model, second to retreve control points data
        cp_response = rest_api_request(cp_analysis)
        geo_api_response = rest_api_request(cp_stats)


        # Set metric value for promethues scraping
        level1_count_g.set(geo_api_response['level1_count'])
        level2_count_g.set(geo_api_response['level2_count'])
        level3_count_g.set(geo_api_response['level3_count'])

        level1_pc_g.set(geo_api_response['level1_pc'])
        level2_pc_g.set(geo_api_response['level2_pc'])
        level3_pc_g.set(geo_api_response['level3_pc'])

        level1_time_g.set(geo_api_response['level1_time'])
        level2_time_g.set(geo_api_response['level2_time'])
        level3_time_g.set(geo_api_response['level3_time'])
        time.sleep(300)
        '''
        level1_g.inc()
        level2_g.inc()
        level3_g.inc()
        print(level1_g)
        print(level2_g)
        print(level3_g)
        time.sleep(5)
        '''