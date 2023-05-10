import yaml
import pandas as pd
import pyproj, csv, decimal
'''
Data source:
Sitetrakcer
Orion network yaml file: https://github.com/swift-nav/skylark-networks/blob/master/networks.yaml
Grafana station signal for different regions:

Update and reiew production layer before deployed to RDS PostGIS database
'''

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
def dataframe_cleanup(region):
    input_stations_prod = '/Users/dj/Documents/postgis/csv/{}_stations_prod.csv'.format(region)
    output_stations_prod = '/Users/dj/Documents/postgis/csv/{}_stations_prod_clean.csv'.format(region)

    station_df = pd.read_csv(input_stations_prod)
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

    station_df.to_csv(output_stations_prod, index=False)


def join_station_signal(region):
    station_signals = '/Users/dj/Documents/postgis/csv/{}_signals.csv'.format(region)
    output_stations_prod = '/Users/dj/Documents/postgis/csv/{}_stations_prod.csv'.format(region)

    station_base_df = pd.read_csv('/Users/dj/Documents/QGIS/yaml/stations_base_wgs.csv')
    st_df = pd.read_csv(station_signals)
    merged = station_base_df.merge(st_df, on="Station", how='left')
    merged.to_csv(output_stations_prod, index=False)


# Read base station and rover station from yaml file
def base_rover_cleaner(region):
    index = region.lower()
    input_yaml = '/Users/dj/Documents/QGIS/yaml/networks.yaml'
    output_base = '/Users/dj/Documents/QGIS/yaml/{}_stations_base.csv'.format(region)
    output_rover = '/Users/dj/Documents/QGIS/yaml/{}_stations_rover.csv'.format(region)

    with open(input_yaml, 'r') as f:
        with open(output_base, 'w') as newcsvfile:
            # initialize cursor
            doc = yaml.load(f, Loader=yaml.FullLoader)
            writer = csv.writer(newcsvfile, delimiter=',')

            # write first row
            writer.writerow(['Station'])

            stationlist = doc[index]['prod']['base']
            for item in stationlist:
                print(item['identifier'])
                writer.writerow([item['identifier']])

    with open(input_yaml, 'r') as f:
        with open(output_rover, 'w') as newcsvfile:
            # initialize cursor
            doc = yaml.load(f, Loader=yaml.FullLoader)
            writer = csv.writer(newcsvfile, delimiter=',')

            # write first row
            writer.writerow(['Station'])

            stationlist = doc[index]['prod']['rover']
            for item in stationlist:
                print(item['identifier'])
                writer.writerow([item['identifier']])


# Join base station and rover station list with geo info from sitetracker
def geo_information_join(region):

    input_base = '/Users/dj/Documents/QGIS/yaml/{}_stations_base.csv'.format(region)
    input_rover = '/Users/dj/Documents/QGIS/yaml/{}_stations_rover.csv'.format(region)
    all_stations = '/Users/dj/Documents/QGIS/yaml/all_stations.csv'

    station_base_df = pd.read_csv(input_base)
    st_df = pd.read_csv(all_stations)
    merged = station_base_df.merge(st_df, on="Station")
    merged.to_csv('/Users/dj/Documents/QGIS/yaml/stations_base.csv', index=False)

    station_rover_df = pd.read_csv(input_rover)
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


# Update production layer based on region (NA, EU, AP)
def layer_update(region):
    combine_stations()
    base_rover_cleaner(region)
    geo_information_join(region)

    # Define station base and rover file
    station_base = '/Users/dj/Documents/QGIS/yaml/stations_base.csv'
    station_base_wgs = '/Users/dj/Documents/QGIS/yaml/stations_base_wgs.csv'
    station_rover = '/Users/dj/Documents/QGIS/yaml/stations_rover.csv'
    station_rover_wgs = '/Users/dj/Documents/QGIS/yaml/stations_rover_wgs.csv'

    geocentric_to_geodetic(station_base, station_base_wgs)
    geocentric_to_geodetic(station_rover, station_rover_wgs)

    # The last step to cleanup layer table to match PostGIS schema
    join_station_signal(region)
    dataframe_cleanup(region)


# Calculate Distance matrix between base stations and rover stations
def distance_matrix():
    print('test')

if __name__ == '__main__':
    layer_update('EU')
