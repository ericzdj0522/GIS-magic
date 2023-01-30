import requests
import psycopg2
import json
import config

# PR test for new repo on Github
# Send http request via port-forward to prometheous database
def prometheous_post_request():
    URL="http://localhost:9999/api/v1/query"

    query = "sum by (station)(orion_ntrip_client_bytes_sum)"
    #query = "sum by (station)(irate(orion_num_obs_total{geography='eu',code='BDS B1', station='ATFS00AUT'}[1m]))"

    PARAMS = {"query": query}

    r = requests.get(url = URL, params = PARAMS)
    data = r.json()

    station_status = data['data']['result']
    station_dic = {}

    # Serializing json
    for station in station_status:
        station_dic[station['metric']['station']] = station['value'][1]

    print(station_dic)
    json_object = json.dumps(station_dic, indent=4)

    # Writing to sample.json
    with open("/Users/dj/Documents/AWS/Test/sample.json", "w") as outfile:
        outfile.write(json_object)


# Load json sample into Postgis database
def json_parser(test):
    f = open('/Users/dj/Documents/AWS/Test/sample.json')
    data = json.load(f)

    if test==0:
        for station, status in data.items():
            print(station)
            update_postgis('0', station)
    else:
        for station, status in data.items():
            print(station)
            update_postgis(status, station)
    #Test case

    f.close()


# Postgis connection
def select_postgis():
    #sql to perform her
    sql = 'SELECT "bds-b1" FROM "swift"."CONUS_stations_v2"'
    sqlupdate = 'UPDATE "swift"."CONUS_stations_v2" SET "bds-b1" = %s WHERE "station" = %s'
    print("test")
    #build database connection
    conn = psycopg2.connect(user="",
                            password="",
                            host="127.0.0.1",
                            port="5432",
                            database="postgis_test")

    #Initialize cursor
    cur = conn.cursor()


    cur.execute(sql)
    record = cur.fetchall()
    length = len(record)
    print(record)
    print(length)

    conn.commit()
    cur.close()

#Postgis update process
def update_postgis(status, station):
    #sql to perform her
    try:
        sql = 'UPDATE "swift"."EU_stations_v2" SET "status" = %s WHERE "station" = %s'
        print(sql)
        # build database connection
        conn = psycopg2.connect(user="",
                                password="",
                                host="127.0.0.1",
                                port="5432",
                                database="postgis_test")

        # Initialize cursor
        cur = conn.cursor()
        cur.execute(sql, (status, station))
        conn.commit()
        cur.close()

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)

    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


#Main function
if __name__ == '__main__':
    #Send request to prometheous database to pull out station data
    prometheous_post_request()
    # Test case for station status: 0 to rest station layer; 1 to load prometheous data to postgis for real time station status
    json_parser(1)

