# coding=utf-8
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.



import pyproj, csv, decimal

def geoconversion(x, y, z):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, alt = pyproj.transform(ecef, lla, x, y, z, radians=False)
    return lon, lat, alt


def geoconversion_reverse(long, lat, alt):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x, y, z = pyproj.transform(lla, ecef, long, lat, alt, radians=False)
    return x, y, z


with open('/Users/dj/Documents/QGIS/CSV/Test/Swift_Production_Station_Coordinates.csv') as csvfile:
    with open('/Users/dj/Documents/QGIS/CSV/Test/Swift_Production_Station.csv', 'w') as newcsvfile:
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
            lon, lat, alt = geoconversion(float(row[1]), float(row[2]), float(row[3]))
            print lon, lat, alt
            temp = [lon, lat, alt]
            writer.writerow(row + temp)
'''

with open('/Users/dj/Documents/QGIS/CSV/Autstralia/AUSCORS_stations_total.csv') as csvfile:
    with open('/Users/dj/Documents/QGIS/CSV/Autstralia/AUSCORS_stations_total_update.csv', 'w') as newcsvfile:
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
            x, y, z = geoconversion_reverse(float(row[14]), float(row[15]), float(row[16]))
            print x, y, z
            temp = [x, y, z]
            writer.writerow(row + temp)

'''






#print lat, lon, alt

