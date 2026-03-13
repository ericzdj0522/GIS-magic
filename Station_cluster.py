import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import csv
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import euclidean

def number_to_letters(n):
    result = ''
    if n == 0 :
        result = 'A'
        return result
    while n > 0:
        #n -= 1  # Adjust because there's no 0 in this system
        result = chr(n % 26 + ord('A')) + result
        n //= 26
    return result

#Read source csv file
df = pd.read_csv("/Users/dj/Documents/QGIS/CSV/NA/02262025/Cluster/NA_stations_coords.csv", usecols=[2, 3])

# Convert to a NumPy array
stationarray = df.to_numpy()

print(stationarray)

# Sample Data: (x, y) coordinates of points
points = stationarray

# Minimum allowed distance between points in a group, List of clusters (each cluster is a list of point indices)
min_distance = 600000
clusters = []

# Greedy clustering algorithm
for i, point in enumerate(points):
    assigned = False

    # Try to add the point to an existing cluster
    for cluster in clusters:
        if all(euclidean(point, points[idx]) >= min_distance for idx in cluster):
            cluster.append(i)
            assigned = True
            break

    # If the point could not be added to any cluster, create a new one
    if not assigned:
        clusters.append([i])

#read as dictionary
df = pd.read_csv("/Users/dj/Documents/QGIS/CSV/NA/02262025/Cluster/NA_stations_coords.csv")
# Convert the DataFrame to a dictionary with 'ID' as the key and coordinates (X, Y) as the value
coord_dict = {(row['x'], row['y']) : row['station'] for _, row in df.iterrows()}
# Display the dictionary
print(coord_dict)

#Output cluster into csv file
with open("/Users/dj/Documents/QGIS/CSV/NA/02262025/Cluster/NA_stations_cluster.csv", mode="w") as file:
    writer = csv.writer(file)
    for cluster_id, cluster in enumerate(clusters):
        letter = number_to_letters(cluster_id)
        stationlist = []
        for i in cluster:
            stationlist.append(coord_dict[tuple(points[i])])
        #Output each cluster as a row
        writer.writerow(["Cluster " + str(letter)] + stationlist)
        print(letter)
        print(f"Cluster {letter}:" + str(stationlist))
    #print(f"Cluster {cluster_id}: {[points[i] for i in cluster]}")



#Ploting assigned clusters
# 🎨 Assign random colors to clusters
colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(len(clusters))]

# 📊 Plot the clusters
plt.figure(figsize=(8, 6))
for cluster_id, cluster in enumerate(clusters):
    if cluster_id:
        cluster_points = points[cluster]
        x, y = cluster_points[:, 0], cluster_points[:, 1]
        plt.scatter(x, y, color=colors[cluster_id], label=f'Cluster {cluster_id}', edgecolors='black')

# 📌 Formatting
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Greedy Clustering with Minimum Distance")
plt.legend()
plt.grid(True)
plt.show()

# Print results
'''


# DBSCAN Clustering (eps = minimum distance, min_samples = minimum points to form a cluster)
eps_value = 100000# Minimum distance threshold
min_samples = 1# Minimum points to form a cluster
db = DBSCAN(eps=eps_value, min_samples=min_samples).fit(points)

# Assign cluster labels
labels = db.labels_

# Convert to DataFrame for better visualization
df = pd.DataFrame(points, columns=["X", "Y"])
df["Cluster"] = labels

print(df)

# Plot clusters
plt.scatter(points[:, 0], points[:, 1], c=labels, cmap="viridis", edgecolors="k")
plt.title("DBSCAN Clustering (Minimum Distance Based)")
plt.show()
'''