class Configuration:
    RAW_DATA_PATH = "./data/{}/raw/"
    EXTRACTED_DATA_PATH = "./data/{}/extracted/"
    CLEANSED_DATA_PATH = "./data/{}/cleansed/"
    DP_DATA_PATH = "./data/{}/{}/"
    TARGET_INTERVAL = 60
    GPS_LIMITS = {
        "geo_life": {'lat': (39.6, 40.1), 'lng': (116.0, 116.8)},
        "taxi": {'lat': (-8.99, -7.00), 'lng':  (38.56, 42.10)},
        "oldenburg": {'lat': (281.0, 23854.1), 'lng': (3935.0, 30851.1)},
        "san_joaquin": {'lat': (3420584.0, 4077155.1), 'lng': (4725764.0, 5442669.1)}
    }
    GPS_LIMIT = {'lat': (39.6, 40.1), 'lng': (116.0, 116.8)}
    LENGTH_RANGE = {
        "geo_life": list(range(500, 12000, 500)),
        "taxi": list(range(500, 4000, 500)),
        "oldenburg": list(range(500, 3500, 500)),
        "san_joaquin": list(range(500, 3500, 500))
    }
    GRID_SIZE = 300
    NEIGHBOR_RANGE = 1
    LENGTH_LIMIT = 1000
    DELTA_DP = 0.01

    TAU = 0.005
    THETA = 0.5

    MAX_SCORE_DIFFERENCE = 0.01

    SCALE = 3

    BS_BLOCKS = 10
    BS_BLOCK_SIZE = 5

    PURE_BS_BLOCK_SIZE = 1

    TD_OMEGA = 0.01


    TARGET_COUNT_EACH_CATEGORY = 20

    QUERY_REP_COUNT = 200

