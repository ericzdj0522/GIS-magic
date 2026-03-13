import json
import csv

def json_to_csv(json_file, csv_file):
    # Open the JSON file and load its content
    with open(json_file, 'r') as f:
        data = json.load(f)
        station_status = data['data']['result']
        print(station_status)


    # Open the CSV file in write mode
    with open(csv_file, 'w') as f:
        # Create a CSV writer object
        writer = csv.writer(f)


        # Write each row of data
        for station in station_status:
            print(station['metric']['station'] + station['value'][1])
            writer.writerow([station['metric']['station'], station['value'][1]])

# Usage example:
jsonfile = '/Users/dj/Documents/QGIS/CSV/NA/0501/na_station_status.json'
csvfile = '/Users/dj/Documents/QGIS/CSV/NA/0501/na_station_status_clean.csv'
json_to_csv(jsonfile, csvfile)