from imports import *
from configuration import *
from distance import *
from coordinates import *


class TrajectoryUtil:

    @staticmethod
    def show_trajectory(trajectory):
        plt.plot(*np.array(trajectory)[:,:2].T)
        plt.show()

    @staticmethod
    def read_trajectory(file_name):
        with open(file_name, "r") as f:
            return json.load(f)

    @staticmethod
    def filter_trajectory_in_range(trajectory, gps_limit):

        for lat, lng, _ in trajectory:
            if gps_limit["lat"][0] <= lat < gps_limit["lat"][1] and \
                gps_limit["lng"][0] <= lng < gps_limit["lng"][1]:
                continue
            return False
        else:
            return True

    @staticmethod
    def filter_trajectory_in_length(trajectory, length_limit = Configuration.LENGTH_LIMIT):
        if len(trajectory) < length_limit:
            return False
        return True

    @staticmethod
    def cut_trajectory(trajectory):
        assert len(trajectory) >= Configuration.LENGTH_LIMIT
        return trajectory[:1000]

    @staticmethod
    def smooth_trajectory(trajectory, interval = None):

        if not interval:
            interval = Configuration.TARGET_INTERVAL
        new_trajectory = []
        x, y, time = trajectory[0]
        time_shift = time
        last_time = 0
        new_trajectory.append((x, y, last_time))
        last_x, last_y,_ = new_trajectory[-1]
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
        cell_trajectory = []
        for x, y, tt in trajectory:
            x_cell, y_cell = Coordinates.get_cell((x, y))
            cell_trajectory.append((x_cell, y_cell, tt))
        return cell_trajectory


    @staticmethod
    def project_cell_to_grid(x_cell, y_cell, new_grid_size):
        return int(x_cell / Configuration.GRID_SIZE * new_grid_size), int(y_cell / Configuration.GRID_SIZE * new_grid_size)

    @staticmethod
    def project_trajectory_to_grid(trajectory, new_grid_size):
        cell_trajectory = []
        for x_cell, y_cell, tt in trajectory:
            x_cell, y_cell = TrajectoryUtil.project_cell_to_grid(x_cell, y_cell, new_grid_size)
            cell_trajectory.append((x_cell, y_cell, tt))
        return cell_trajectory


    @staticmethod
    def calc_trajectory_length(trajectory):
        length = 0
        for prev_point, curr_point in zip(trajectory, trajectory[1:]):
            length += Distance.sq_euclidean(prev_point, curr_point)
        return length

    @staticmethod
    def add_time(trajectory):
        trajectory_with_time = []
        for prev_point, curr_point in zip(trajectory, trajectory[1:]):
            if trajectory_with_time:
                trajectory_with_time += list(bresenham(prev_point[0], prev_point[1], curr_point[0], curr_point[1]))[1:]
            else:
                trajectory_with_time += list(bresenham(prev_point[0], prev_point[1], curr_point[0], curr_point[1]))
        return list(map(lambda idx: (trajectory_with_time[idx][0], trajectory_with_time[idx][1], idx), range(len(trajectory_with_time))))