from imports import *
from configuration import *

class Coordinates:
    """
    A utility class for working with geographical coordinates and grid cells.
    """

    @staticmethod
    def in_range(point):
        """
        Checks if a given point is within the defined GPS limits.

        Args:
            point (tuple): The geographical point represented as a tuple (latitude, longitude).

        Returns:
            bool: True if the point is within the GPS limits, False otherwise.
        """
        x, y = point[0], point[1]
        if Configuration.GPS_LIMIT['lat'][0] <= x < Configuration.GPS_LIMIT['lat'][1] and \
                Configuration.GPS_LIMIT['lng'][0] <= y < Configuration.GPS_LIMIT['lng'][1]:
            return True

    @staticmethod
    def in_range_cell(cell):
        """
        Checks if a given grid cell is within the defined grid size.

        Args:
            cell (tuple): The grid cell represented as a tuple (x, y).

        Returns:
            bool: True if the cell is within the grid size, False otherwise.
        """
        x, y = cell[0], cell[1]
        return 0 <= x < Configuration.GRID_SIZE and 0 <= y < Configuration.GRID_SIZE

    @staticmethod
    def get_cell(point, grid_size=None):
        """
        Converts a geographical point to its corresponding grid cell.

        Args:
            point (tuple): The geographical point represented as a tuple (latitude, longitude).
            grid_size (int): The size of the grid (optional).

        Returns:
            tuple: The grid cell corresponding to the given point as a tuple (x, y).
        """
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
        """
        Calculates the distance (cell difference) between two grid cells.

        Args:
            point1 (tuple): The first grid cell represented as a tuple (x1, y1).
            point2 (tuple): The second grid cell represented as a tuple (x2, y2).

        Returns:
            int: The cell distance between the two points.
        """
        return max(abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))

    @staticmethod
    def get_cell_corners(cell):
        """
        Retrieves the corner coordinates of a given grid cell.

        Args:
            cell (tuple): The grid cell represented as a tuple (x, y).

        Returns:
            list: A list of corner coordinates [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
        """
        x, y = cell[0], cell[1]
        return [(x-0.5, y-0.5), (x-0.5, y+0.5), (x+0.5, y-0.5), (x+0.5, y+0.5)]

    @staticmethod
    def get_coordinate(cell):
        """
        Converts a grid cell to its corresponding geographical coordinate.

        Args:
            cell (tuple): The grid cell represented as a tuple (x, y).

        Returns:
            tuple: The geographical coordinate corresponding to the given cell as a tuple (latitude, longitude).
        """
        assert Coordinates.in_range_cell(cell)
        x, y = cell[0], cell[1]
        x_step = (Configuration.GPS_LIMIT['lat'][1] - Configuration.GPS_LIMIT['lat'][0]) / Configuration.GRID_SIZE
        y_step = (Configuration.GPS_LIMIT['lng'][1] - Configuration.GPS_LIMIT['lng'][0]) / Configuration.GRID_SIZE

        coordinate_x = Configuration.GPS_LIMIT['lat'][0] + x_step * x
        coordinate_y = Configuration.GPS_LIMIT['lng'][0] + y_step * y

        return coordinate_x, coordinate_y
