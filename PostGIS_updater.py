import yaml
import csv
import pandas as pd
import pyproj, csv, decimal


#Define global variables here

# Combine first and third party stations from Sitetracker
def combine_stations():
    swift_station_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/ST_swift_stations.csv')
    other_station_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/Third_party_stations.csv')
    dts = [swift_station_df, other_station_df]
    all_station_df = pd.concat(dts, ignore_index=False, join='inner')
    all_station_df.to_csv('/Users/dj/Documents/QGIS/yaml/all_stations.csv', index=False)


# Geocentric to Geodetic conversion
def geoconversion(x, y, z):
    ecef = {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'}
    lla = {"proj":'latlong', "ellps":'WGS84', "datum":'WGS84'}
    transformer = pyproj.Transformer.from_crs(ecef, lla)
    #lon, lat, alt = pyproj.transform(ecef, lla, x, y, z, radians=False)
    lon, lat, alt = transformer.transform(x, y, z, radians=False)
    return lon, lat, alt


# Clean up data table to match PostGIS schema
def dataframe_cleanup():
    station_df = pd.read_csv('/Users/dj/Documents/postgis/csv/EU_stations_prod.csv')
    station_df.pop('X')
    station_df.pop('Y')
    station_df.pop('Z')
    station_df.pop('connection')
    station_df['type'] = 'single'
    station_df.columns = station_df.columns.str.lower()
    station_df = station_df.rename(columns={"bds-b1i": "bds-b1", "bds-b2i": "bds-b2"})
    for index in station_df.index:
        if '-' in station_df.at[index, 'station']:
            temp = station_df.at[index, 'station'].split('-')
            station_df.at[index, 'provider'] = temp[0]

        else:
            station_df.at[index, 'provider'] = 'swift'
            station_df.at[index, 'type'] = 'integrity'

    station_df.to_csv('/Users/dj/Documents/postgis/csv/EU_stations_prod_clean.csv', index=False)


def join_station_signal():
    station_base_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/stations_base_wgs.csv')
    st_df = pd.read_csv('/Users/dj/Documents/postgis/csv/EU_signals.csv')
    merged = station_base_df.merge(st_df, on="Station", how='left')
    merged.to_csv('/Users/dj/Documents/postgis/csv/EU_stations_prod.csv', index=False)


# Read base station and rover station from yaml file
def base_rover_cleaner():
    with open('/Users/dj/Documents/QGIS/yaml/networks.yaml', 'r') as f:
        with open('/Users/dj/Documents/QGIS/yaml/EU_stations_base.csv', 'w') as newcsvfile:
            # initialize cursor
            doc = yaml.load(f, Loader=yaml.FullLoader)
            writer = csv.writer(newcsvfile, delimiter=',')

            # write first row
            writer.writerow(['Station'])

            stationlist = doc['eu']['prod']['base']
            for item in stationlist:
                print(item['identifier'])
                writer.writerow([item['identifier']])

    with open('/Users/dj/Documents/QGIS/yaml/networks.yaml', 'r') as f:
        with open('/Users/dj/Documents/QGIS/yaml/EU_stations_rover.csv', 'w') as newcsvfile:
            # initialize cursor
            doc = yaml.load(f, Loader=yaml.FullLoader)
            writer = csv.writer(newcsvfile, delimiter=',')

            # write first row
            writer.writerow(['Station'])

            stationlist = doc['eu']['prod']['rover']
            for item in stationlist:
                print(item['identifier'])
                writer.writerow([item['identifier']])


# Join base station and rover station list with geo info from sitetracker
def geo_information_join():
    station_base_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/EU_stations_base.csv')
    st_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/all_stations.csv')
    merged = station_base_df.merge(st_df, on="Station")
    merged.to_csv('/Users/dj/Documents/QGIS/yaml/stations_base.csv', index=False)

    station_rover_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/EU_stations_rover.csv')
    merged = station_rover_df.merge(st_df, on="Station")
    merged.to_csv('/Users/dj/Documents/QGIS/yaml/stations_rover.csv', index=False)


# Convert geocentric coordinates to geodetic coordinates
def geocentric_to_geodetic(input, output):
    with open(input) as csvfile:
        with open(output, 'w') as newcsvfile:
            cursor = csv.reader(csvfile, delimiter=',')
            writer = csv.writer(newcsvfile, delimiter=',')
            firstline = True
            for row in cursor:
                if row[1] == '':
                    writer.writerow(row)
                    continue
                if firstline:
                    firstline = False
                    writer.writerow(row + ['longitude', 'latitude', 'altitude', 'provider', 'pilot', 'commercial', 'access', 'sla', 'base', 'rover'])
                    continue
                lon, lat, alt = geoconversion(float(row[1]), float(row[2]), float(row[3]))
                temp = [lon, lat, alt, 'temp', '1', '1', '1', '100', '1', '0']
                writer.writerow(row + temp)


# Calculate Distance matrix between base stations and rover stations
def distance_matrix():
    print('test')

if __name__ == '__main__':

    combine_stations()
    base_rover_cleaner()
    geo_information_join()
    station_base = '/Users/dj/Documents/QGIS/yaml/stations_base.csv'
    station_base_wgs = '/Users/dj/Documents/QGIS/yaml/stations_base_wgs.csv'
    station_rover = '/Users/dj/Documents/QGIS/yaml/stations_rover.csv'
    station_rover_wgs = '/Users/dj/Documents/QGIS/yaml/stations_rover_wgs.csv'
    geocentric_to_geodetic(station_base, station_base_wgs)
    geocentric_to_geodetic(station_rover, station_rover_wgs)
    join_station_signal()

    dataframe_cleanup()
