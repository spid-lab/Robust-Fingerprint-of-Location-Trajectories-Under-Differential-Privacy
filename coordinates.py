from imports import *
from configuration import *

class Coordinates:


    @staticmethod
    def in_range(point):
        x, y = point[0], point[1]
        if Configuration.GPS_LIMIT['lat'][0] <= x < Configuration.GPS_LIMIT['lat'][1] and \
                Configuration.GPS_LIMIT['lng'][0] <= y < Configuration.GPS_LIMIT['lng'][1]:
            return True

    @staticmethod
    def in_range_cell(cell):
        x, y = cell[0], cell[1]
        return 0 <= x < Configuration.GRID_SIZE and 0 <= y < Configuration.GRID_SIZE

    @staticmethod
    def get_cell(point, grid_size = None):
        assert Coordinates.in_range(point), point

        if not grid_size:
            grid_size = Configuration.GRID_SIZE
        x_step = (Configuration.GPS_LIMIT['lat'][1] - Configuration.GPS_LIMIT['lat'][0]) / grid_size
        y_step = (Configuration.GPS_LIMIT['lng'][1] - Configuration.GPS_LIMIT['lng'][0]) / grid_size
        x_id = int((point[0] - Configuration.GPS_LIMIT['lat'][0]) / x_step)
        y_id = int((point[1] - Configuration.GPS_LIMIT['lng'][0]) / y_step)
        return x_id, y_id

    @staticmethod
    def get_cell_distance(point1, point2):
        return max(abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))

    @staticmethod
    def get_cell_corners(cell):
        x, y = cell[0], cell[1]
        return [(x-0.5, y-0.5), (x-0.5, y+0.5), (x+0.5, y-0.5), (x+0.5, y+0.5)]

    @staticmethod
    def get_coordinate(cell):
        assert Coordinates.in_range_cell(cell)
        x, y = cell[0], cell[1]
        x_step = (Configuration.GPS_LIMIT['lat'][1] - Configuration.GPS_LIMIT['lat'][0]) / Configuration.GRID_SIZE
        y_step = (Configuration.GPS_LIMIT['lng'][1] - Configuration.GPS_LIMIT['lng'][0]) / Configuration.GRID_SIZE

        coordinate_x = Configuration.GPS_LIMIT['lat'][0] + x_step * x
        coordinate_y = Configuration.GPS_LIMIT['lng'][0] + y_step * y

        return coordinate_x, coordinate_y