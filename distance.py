from imports import *
from configuration import *
from distance import *
import math

class Distance:
    @staticmethod
    def sq_euclidean(point_1, point_2):
        x_1, y_1 = point_1[0], point_1[1]
        x_2, y_2 = point_2[0], point_2[1]
        return (x_1 - x_2) ** 2 + (y_1 - y_2) ** 2

    @staticmethod
    def euclidean(point_1, point_2):
        return math.sqrt(Distance.sq_euclidean(point_1, point_2))

    @staticmethod
    def haversine(coord1, coord2):
        radius = 6372800 
        lat1, lng1 = coord1
        lat2, lng2 = coord2

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi     = math.radians(lat2 - lat1)
        delta_lambda    = math.radians(lng2 - lng1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

        return 2*radius*math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def jsd(hist1, hist2):
        return jensenshannon(hist1, hist2)