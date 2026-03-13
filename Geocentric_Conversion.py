# coding=utf-8
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



import pyproj, csv, decimal


def geoconversion(x, y, z):
    transformer = pyproj.Transformer.from_crs(
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
    )
    lon, lat, alt = transformer.transform(x, y, z, radians=False)


    #lon, lat, alt = pyproj.transform(ecef, lla, x, y, z, radians=False)
    return lon, lat, alt


def geoconversion_reverse(long, lat, alt):
    transformer = pyproj.Transformer.from_crs(
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
    )
    x, y, z = transformer.transform(long, lat, alt, radians = False)

    #x, y, z = pyproj.transform(lla, ecef, long, lat, alt, radians=False)
    return x, y, z


with open('/Users/dj/Documents/QGIS/CSV/AP/CSV/CHC_stations_ingestion_ap.csv') as csvfile:
    with open('/Users/dj/Documents/QGIS/CSV/AP/CSV/CHC_stations_ingestion_ap_latlon.csv', 'w') as newcsvfile:
        cursor = csv.reader(csvfile, delimiter=',')
        writer = csv.writer(newcsvfile, delimiter=',')
        firstline = True
        for row in cursor:
            if row[1] == '':
                writer.writerow(row)
                continue
            if firstline:
                firstline = False
                writer.writerow(row + ['Longitude', 'Latitude', 'Altitude'])
                continue
            lon, lat, alt = geoconversion(float(row[6]), float(row[7]), float(row[8]))
            print(lon, lat, alt)
            temp = [lon, lat, alt]
            writer.writerow(row + temp)
'''

with open('/Users/dj/Documents/QGIS/CSV/NA/12042024/stations_to_evaluate.csv') as csvfile:
    with open('/Users/dj/Documents/QGIS/CSV/NA/12042024/stations_to_evaluate_xyz.csv', 'w') as newcsvfile:
        cursor = csv.reader(csvfile, delimiter=',')
        writer = csv.writer(newcsvfile, delimiter=',')
        firstline = True
        for row in cursor:
            if row[1] == '':
                writer.writerow(row)
                continue
            if firstline:
                firstline = False
                writer.writerow(row + ['X', 'Y', 'Z'])
                continue
            x, y, z = geoconversion_reverse(float(row[11]), float(row[10]), float(row[12]))
            print(x, y, z)
            temp = [x, y, z]
            writer.writerow(row + temp)

'''




#print lat, lon, alt

