import csv, geohash2

input_csv = '/Users/dj/Documents/QGIS/CSV/NA/0205/Active_clients2.csv'
output_csv = '/Users/dj/Documents/QGIS/CSV/NA/0205/Active_clients_latlon2.csv'

with open(input_csv) as csvfile:
    with open(output_csv, 'w') as newcsvfile:
        cursor = csv.reader(csvfile, delimiter=',')
        writer = csv.writer(newcsvfile, delimiter=',')

        firstline = True
        for row in cursor:
            if len(row) == 0:
                writer.writerow(row)
                continue
            if firstline:
                firstline = False
                writer.writerow(row + ['longitude', 'latitude'])
                continue
            y, x = geohash2.decode(row[1])
            print(x, y)
            print(len(row))
            temp = [x, y]
            writer.writerow(row + temp)

