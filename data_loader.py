from imports import *
from configuration import *

class DataLoader:



    @staticmethod
    def load_dp_data(dataset, epsilon, method = "pim", index = 0):
        print("Loading dp data...")
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.DP_DATA_PATH.format(dataset.value, method), "{}_{:.3f}_{}.dat".format(dataset.value, epsilon, index)), "r") as f:
            return json.load(f)


    @staticmethod
    def load_correlation_data(dataset, index):
        print("Loading correlation data...")
        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.CLEANSED_DATA_PATH.format(dataset.value), "correlation_trajectories_{}.dat".format(index)), "r") as f:
            return json.load(f)


    @staticmethod
    def load_experimental_data(dataset, index):

        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]
        with open(PurePath(Configuration.CLEANSED_DATA_PATH.format(dataset.value), "exp_trajectories_{}.dat".format(index)), "r") as f:
            return json.load(f)


    @staticmethod
    def load_extracted_data(dataset):

        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]

        with open(Path(Configuration.EXTRACTED_DATA_PATH.format(dataset.value), "extracted_trajectories.dat"), "r") as f:
            return json.load(f)
