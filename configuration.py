class Configuration:
    RAW_DATA_PATH = "./data/{}/raw/"

    EXTRACTED_DATA_PATH = "./data/{}/extracted/"

    CLEANSED_DATA_PATH = "./data/{}/cleansed/"

    DP_DATA_PATH = "./data/{}/{}/"

    TARGET_INTERVAL = 60
    # Time interval in seconds for preprocessing.

    GPS_LIMITS = {
        "geo_life": {"lat": (39.6, 40.1), "lng": (116.0, 116.8)},
        "taxi": {"lat": (-8.99, -7.00), "lng": (38.56, 42.10)},
        "oldenburg": {"lat": (281.0, 23854.1), "lng": (3935.0, 30851.1)},
        "san_joaquin": {"lat": (3420584.0, 4077155.1), "lng": (4725764.0, 5442669.1)},
    }
    # Latitude and longitude limits of each dataset.

    LENGTH_RANGE = {
        "geo_life": list(range(500, 12000, 500)),
        "taxi": list(range(500, 4000, 500)),
        "oldenburg": list(range(500, 3500, 500)),
        "san_joaquin": list(range(500, 3500, 500)),
    }
    # Trajectory lengths for preprocessing.

    GRID_SIZE = 300
    # Grid size used for spatial grid construction.

    NEIGHBOR_RANGE = 1
    # Range for neighboring grid cells.

    LENGTH_LIMIT = 1000
    # Limit on the length of trajectories.

    DELTA_DP = 0.01
    # Privacy parameter delta for PIM.

    TAU = 0.005
    # Correlation threshold.

    THETA = 0.5
    # Balancing factor.

    SCALE = 3
    # Scaling factor for point sampling.

    QUERY_REP_COUNT = 200
    # Number of repetitions for a query.

    EVAL_GRID_SIZE = 10
    # Grid size for utility evaluation.
