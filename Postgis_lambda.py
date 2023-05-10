import psycopg2
import urllib3
import json


# Update PostGIS database in RDS
def station_status_updator(test):
    station_dic = station_status_request('eu_stations_status_metrics.json')

    # Test case for station status: 0 to rest station layer; 1 to load prometheous data to postgis for real time station status
    if test == 0:
        for station, status in station_dic.items():
            print(station)
            update_postgis('0', station, 'EU_stations_v2')
    else:
        for station, status in station_dic.items():
            print(station)
            update_postgis(status, station, 'EU_stations_v2')

        # http reqeust for station status from S3 json file


def station_status_request(file_name):
    # Http request to S3
    http = urllib3.PoolManager()
    url = 'https://swift-nav-stations-status.s3.eu-central-1.amazonaws.com/{0}'.format(file_name)
    res = http.request('GET', url)
    data = res.data
    metrics = json.loads(data)
    station_status = metrics['data']['result']
    station_dic = {}

    # Serializing json to dictionary for sation status
    for station in station_status:
        station_dic[station['metric']['station']] = station['value'][1]

    return station_dic


# Update postGIS database
def update_postgis(status, station, layer):
    # sql to perform her
    try:
        sql = 'UPDATE "swift"."{0}" SET "status" = %s WHERE "station" = %s'.format(layer)
        print(sql)
        # build database connection
        conn = psycopg2.connect(user="geoserver",
                                password="hajoo7gizu2toeng7ahyahw8ahBahkee1ia1Ja1i",
                                host="postgisstaging.cq6imc38uzle.us-west-2.rds.amazonaws.com",
                                port="5432",
                                database="postgisstaging")

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


# Select PostGIS database
def select_postgis():
    # sql to perform her
    sql = 'SELECT "bds-b1" FROM "swift"."CONUS_stations_v2"'
    sqlupdate = 'UPDATE "swift"."CONUS_stations_v2" SET "bds-b1" = %s WHERE "station" = %s'
    print("test")
    # build database connection
    conn = psycopg2.connect(user="geoserver",
                            password="hajoo7gizu2toeng7ahyahw8ahBahkee1ia1Ja1i",
                            host="postgisstaging.cq6imc38uzle.us-west-2.rds.amazonaws.com",
                            port="5432",
                            database="postgisstaging")

    # Initialize cursor
    cur = conn.cursor()

    cur.execute(sql)
    record = cur.fetchall()
    length = len(record)
    print(record)
    print(length)

    conn.commit()
    cur.close()


def lambda_handler(event, context):
    station_status_updator(1)