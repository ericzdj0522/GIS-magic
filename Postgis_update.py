import psycopg2
import json
import config

def json_parser():
    f = open('/Users/dj/Documents/QGIS/Json/station_signals.json')
    data = json.load(f)

    print(data)
    for i in data:
        update_postgis(data[i]['bds-b1'], i)

    f.close()

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

def update_postgis(signal, station):
    #sql to perform her
    try:
        sql = 'UPDATE "swift"."CONUS_stations_v2" SET "bds-b1" = %s WHERE "station" = %s'
        print(sql)
        # build database connection
        conn = psycopg2.connect(user="",
                                password="",
                                host="127.0.0.1",
                                port="5432",
                                database="postgis_test")

        # Initialize cursor
        cur = conn.cursor()
        cur.execute(sql, (signal, station))
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





if __name__ == '__main__':
    json_parser()
    update_postgis('18.4', 'WALD00USA')