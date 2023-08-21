from imports import *
from configuration import *
import math


class Distance:
    """
    A class for distance calculation.
    """

    @staticmethod
    def sq_euclidean(point_1, point_2):
        """
        Calculates the squared Euclidean distance between two points.

        Args:
            point_1 (tuple): The first point as a tuple (x, y).
            point_2 (tuple): The second point as a tuple (x, y).

        Returns:
            float: The squared Euclidean distance.
        """
        x_1, y_1 = point_1[0], point_1[1]
        x_2, y_2 = point_2[0], point_2[1]
        return (x_1 - x_2) ** 2 + (y_1 - y_2) ** 2

    @staticmethod
    def euclidean(point_1, point_2):
        """
        Calculates the Euclidean distance between two points.

        Args:
            point_1 (tuple): The first point as a tuple (x, y).
            point_2 (tuple): The second point as a tuple (x, y).

        Returns:
            float: The Euclidean distance.
        """
        return math.sqrt(Distance.sq_euclidean(point_1, point_2))

    @staticmethod
    def haversine(coord1, coord2):
        """
        Calculates the Haversine distance between two coordinates.

        Args:
            coord1 (tuple): The first coordinate as a tuple (lat, lng).
            coord2 (tuple): The second coordinate as a tuple (lat, lng).

        Returns:
            float: The Haversine distance.
        """
        radius = 6372800
        lat1, lng1 = coord1
        lat2, lng2 = coord2

        phi1, phi2 = math.radians(lat1), math.radians(lat2)

    @staticmethod
    def jsd(hist1, hist2):
        return jensenshannon(hist1, hist2)
