from imports import *
from configuration import *
from distance import *
from coordinates import *


class TrajectoryUtil:
    """
    Utility class for handling trajectory data.
    """

    @staticmethod
    def show_trajectory(trajectory):
        """
        Plots and displays a trajectory.

        Args:
            trajectory (list): List of trajectory points.
        """
        plt.plot(*np.array(trajectory)[:, :2].T)
        plt.show()

    @staticmethod
    def read_trajectory(file_name):
        """
        Reads a trajectory from a file.

        Args:
            file_name (str): Name of the file.

        Returns:
            list: Trajectory data.
        """
        with open(file_name, "r") as f:
            return json.load(f)

    @staticmethod
    def filter_trajectory_in_range(trajectory, gps_limit):
        """
        Filters a trajectory based on GPS limits.

        Args:
            trajectory (list): Trajectory data.
            gps_limit (dict): GPS limits (latitude and longitude ranges).

        Returns:
            bool: True if the trajectory is within the GPS limits, False otherwise.
        """
        for lat, lng, _ in trajectory:
            if (
                gps_limit["lat"][0] <= lat < gps_limit["lat"][1]
                and gps_limit["lng"][0] <= lng < gps_limit["lng"][1]
            ):
                continue
            return False
        else:
            return True

    @staticmethod
    def filter_trajectory_in_length(
        trajectory, length_limit=Configuration.LENGTH_LIMIT
    ):
        """
        Filters a trajectory based on its length.

        Args:
            trajectory (list): Trajectory data.
            length_limit (int): Minimum length limit.

        Returns:
            bool: True if the trajectory is longer than the length limit, False otherwise.
        """
        if len(trajectory) < length_limit:
            return False
        return True

    @staticmethod
    def cut_trajectory(trajectory):
        """
        Cuts a trajectory to a specific length.

        Args:
            trajectory (list): Trajectory data.

        Returns:
            list: Cut trajectory data.
        """
        assert len(trajectory) >= Configuration.LENGTH_LIMIT
        return trajectory[:1000]

    @staticmethod
    def smooth_trajectory(trajectory, interval=None):
        """
        Smoothes a trajectory.

        Args:
            trajectory (list): Trajectory data.
            interval (float): Time interval between points.

        Returns:
            list: Smoothed trajectory data.
        """
        if not interval:
            interval = Configuration.TARGET_INTERVAL
        new_trajectory = []
        x, y, time = trajectory[0]
        time_shift = time
        last_time = 0
        new_trajectory.append((x, y, last_time))
        last_x, last_y, _ = new_trajectory[-1]
        remainder = interval

        i = 1
        while i < len(trajectory):
            x, y, time = trajectory[i]
            delta_time = (time - time_shift) - last_time
            if remainder > delta_time:
                remainder -= delta_time
                last_x, last_y, last_time = x, y, time - time_shift
                i += 1
            elif remainder == delta_time:
                new_time = new_trajectory[-1][2] + interval
                new_trajectory.append((x, y, new_time))
                remainder = interval
                i += 1
            else:
                percentage = remainder / delta_time
                new_x = last_x + percentage * (x - last_x)
                new_y = last_y + percentage * (y - last_y)
                new_time = new_trajectory[-1][2] + interval

                new_trajectory.append((new_x, new_y, new_time))
                last_x, last_y, last_time = new_x, new_y, new_time
                remainder = interval

        return new_trajectory

    @staticmethod
    def point_to_cell(trajectory):
        """
        Converts a trajectory from point coordinates to cell coordinates.

        Args:
            trajectory (list): Trajectory data in point coordinates.

        Returns:
            list: Trajectory data in cell coordinates.
        """
        cell_trajectory = []
        for x, y, tt in trajectory:
            x_cell, y_cell = Coordinates.get_cell((x, y))
            cell_trajectory.append((x_cell, y_cell, tt))
        return cell_trajectory

    @staticmethod
    def project_cell_to_grid(x_cell, y_cell, new_grid_size):
        """
        Projects cell coordinates to a new grid size.

        Args:
            x_cell (int): X-coordinate of the cell.
            y_cell (int): Y-coordinate of the cell.
            new_grid_size (int): New grid size.

        Returns:
            tuple: Projected cell coordinates.
        """
        return (
            int(x_cell / Configuration.GRID_SIZE * new_grid_size),
            int(y_cell / Configuration.GRID_SIZE * new_grid_size),
        )

    @staticmethod
    def project_trajectory_to_grid(trajectory, new_grid_size):
        """
        Projects a trajectory to a new grid size.

        Args:
            trajectory (list): Trajectory data.
            new_grid_size (int): New grid size.

        Returns:
            list: Projected trajectory data.
        """
        cell_trajectory = []
        for x_cell, y_cell, tt in trajectory:
            x_cell, y_cell = TrajectoryUtil.project_cell_to_grid(
                x_cell, y_cell, new_grid_size
            )
            cell_trajectory.append((x_cell, y_cell, tt))
        return cell_trajectory

    @staticmethod
    def calc_trajectory_length(trajectory):
        """
        Calculates the length of a trajectory.

        Args:
            trajectory (list): Trajectory data.

        Returns:
            float: Trajectory length.
        """
        length = 0
        for prev_point, curr_point in zip(trajectory, trajectory[1:]):
            length += Distance.sq_euclidean(prev_point, curr_point)
        return length

    @staticmethod
    def add_time(trajectory):
        """
        Adds time information to a trajectory.

        Args:
            trajectory (list): Trajectory data.

        Returns:
            list: Trajectory data with time information.
        """
        trajectory_with_time = []
        for prev_point, curr_point in zip(trajectory, trajectory[1:]):
            if trajectory_with_time:
                trajectory_with_time += list(
                    bresenham(
                        prev_point[0], prev_point[1], curr_point[0], curr_point[1]
                    )
                )[1:]
            else:
                trajectory_with_time += list(
                    bresenham(
                        prev_point[0], prev_point[1], curr_point[0], curr_point[1]
                    )
                )
        return list(
            map(
                lambda idx: (
                    trajectory_with_time[idx][0],
                    trajectory_with_time[idx][1],
                    idx,
                ),
                range(len(trajectory_with_time)),
            )
        )
