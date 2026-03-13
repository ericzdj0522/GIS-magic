from scipy.spatial.distance import euclidean
import math
import pandas as pd

#Scenario 1
total_distance = 0
def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def check_drone_distance(coordinates):
    for i in range(1, len(coordinates)):
        points1 = coordinates[i-1]
        points2 = coordinates[i]
        total_distance += euclidean(points1, points2)
        if total_distance > 1:
            print("Drone travelled more than x meters")


#Scenario 2
from collections import deque

class HitCounter:
    def __init__(self):
        self.hits = deque()
    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def getHits(self, timestamp: int) -> int:
        #Remove outdated hits
        while self.hits and self.hits[0] <= timestamp - 300
            self.hits.popleft()
        return len(self.hits)