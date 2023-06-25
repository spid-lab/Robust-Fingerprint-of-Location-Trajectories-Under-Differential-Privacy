from imports import *
from configuration import *


class DataLoader:
    """
    A class for loading different types of data.
    """

    @staticmethod
    def load_dp_data(dataset, epsilon, method="pim", index=0):
        """
        Loads differential privacy data for a specific dataset.

        Args:
            dataset (Enum): The dataset to load the data for.
            epsilon (float): The privacy parameter epsilon.
            method (str): The differential privacy method (default: "pim").
            index (int): The index of the data file (default: 0).

        Returns:
            dict: The loaded differential privacy data.
        """
        print("Loading dp data...")
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.DP_DATA_PATH.format(dataset.value, method),
                           "{}_{:.3f}_{}.dat".format(dataset.value, epsilon, index)), "r") as f:
            return json.load(f)

    @staticmethod
    def load_correlation_data(dataset, index):
        """
        Loads correlation data for a specific dataset.

        Args:
            dataset (Enum): The dataset to load the data for.
            index (int): The index of the data file.

        Returns:
            dict: The loaded correlation data.
        """
        print("Loading correlation data...")
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.CLEANSED_DATA_PATH.format(dataset.value),
                           "correlation_trajectories_{}.dat".format(index)), "r") as f:
            return json.load(f)

    @staticmethod
    def load_experimental_data(dataset, index):
        """
        Loads experimental data for a specific dataset.

        Args:
            dataset (Enum): The dataset to load the data for.
            index (int): The index of the data file.

        Returns:
            dict: The loaded experimental data.
        """
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.CLEANSED_DATA_PATH.format(dataset.value),
                           "exp_trajectories_{}.dat".format(index)), "r") as f:
            return json.load(f)

    @staticmethod
    def load_extracted_data(dataset):
        """
        Loads extracted data for a specific dataset.

        Args:
            dataset (Enum): The dataset to load the data for.

        Returns:
            dict: The loaded extracted data.
        """
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(Path(Configuration.EXTRACTED_DATA_PATH.format(dataset.value),
                       "extracted_trajectories.dat"), "r") as f:
            return json.load(f)
