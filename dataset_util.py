from imports import *
from configuration import *
from dataset import *
from data_loader import *
from trajectory_util import *


class DatasetUtil:
    """
    A utility class for dataset operations.
    """

    @staticmethod
    def extract_dataset(dataset):
        """
        Extracts trajectories from raw data for a specific dataset.

        Args:
            dataset (Enum): The dataset to extract trajectories from.
        """
        print("Extracting trajectories from raw data...")
        data_path = Configuration.RAW_DATA_PATH.format(dataset.value)
        out_path = Configuration.EXTRACTED_DATA_PATH.format(dataset.value)
        shutil.rmtree(out_path)

        Configuration.GPS_LIMIT = Configuration.GPS_LIMITS[dataset.value]

        if dataset == Dataset.GEO_LIFE:

            def find_plt(path):
                return list(Path(path).rglob("*.plt"))

            file_names = find_plt(data_path)

            def extract_geo_life_trajectory(file_name, out_file_name, out_file_path):
                with open(file_name, "r") as f:
                    trajectory_data = list(
                        map(
                            lambda line: (
                                float(line[0]),
                                float(line[1]),
                                24 * 3600 * float(line[4]),
                            ),
                            map(lambda line: line.split(","), f.readlines()[6:]),
                        )
                    )

                return trajectory_data

            Path(out_path).mkdir(parents=True, exist_ok=True)
            trajectories = Parallel(n_jobs=16, verbose=1)(
                delayed(extract_geo_life_trajectory)(
                    file,
                    file.name,
                    Configuration.EXTRACTED_DATA_PATH.format(dataset.value),
                )
                for file in file_names
            )

            with open(Path(out_path, "extracted_trajectories.dat"), "w") as f:
                json.dump(trajectories, f)

        elif dataset == Dataset.TAXI:
            file_name = Path(
                Configuration.RAW_DATA_PATH.format(dataset.value), "data.csv"
            )
            data = pd.read_csv(file_name)["POLYLINE"].to_list()

            def add_timestamp(trajectory):
                out_trajectory = []
                for j, (lat, lng) in enumerate(trajectory):
                    out_trajectory.append((lat, lng, j * Configuration.TARGET_INTERVAL))
                return out_trajectory

            trajectories = Parallel(n_jobs=16, verbose=1)(
                delayed(add_timestamp)(json.loads(trajectory_str))
                for i, trajectory_str in enumerate(data)
            )

            Path(out_path).mkdir(parents=True, exist_ok=True)
            with open(Path(out_path, "extracted_trajectories.dat"), "w") as f:
                json.dump(trajectories, f)

        elif dataset == Dataset.OLDENBURG or dataset == Dataset.SAN_JOAQUIN:
            with open(Path(data_path, "raw_trajectories.dat"), "r") as f:
                lines = f.readlines()

            trajectories = {}
            for line in lines:
                (
                    flag,
                    trajectory_id,
                    seq_id,
                    class_id,
                    t,
                    x,
                    y,
                    speed,
                    next_x,
                    next_y,
                ) = line.split("\t")
                trajectory_id, x, y, t = int(trajectory_id), float(x), float(y), int(t)
                if flag == "newpoint":
                    trajectories[trajectory_id] = [(x, y, t)]
                else:
                    trajectories[trajectory_id].append((x, y, t))

            trajectories = [trajectories[idx] for idx in trajectories.keys()]
            Path(out_path).mkdir(parents=True, exist_ok=True)
            with open(Path(out_path, "extracted_trajectories.dat"), "w") as f:
                json.dump(trajectories, f)
        print("Extraction OK.")

    @staticmethod
    def generate_experimental_and_correlation_dataset(dataset, copies=5):
        """
        Generates experimental and correlation datasets for a specific dataset.

        Args:
            dataset (Enum): The dataset to generate the datasets for.
            copies (int): The number of dataset copies to generate (default: 5).
        """

        raw_trajectories = DataLoader.load_extracted_data(dataset)

        print("Cleansing and generating experimental datasets...")
        range_restricted_trajectories = list(
            filter(
                lambda x: TrajectoryUtil.filter_trajectory_in_range(
                    x, Configuration.GPS_LIMIT
                ),
                raw_trajectories,
            )
        )

        out_path = Configuration.CLEANSED_DATA_PATH.format(dataset.value)
        shutil.rmtree(out_path)
        Path(out_path).mkdir(parents=True, exist_ok=True)

        for index in tqdm(range(copies)):
            correlation_trajectories = []
            exp_trajectories = []

            for trajectory in range_restricted_trajectories:
                if not TrajectoryUtil.filter_trajectory_in_length(trajectory, 500):
                    correlation_trajectories.append(trajectory)
                else:
                    exp_trajectories.append(trajectory)

            selected_indexes = random.choice(
                range(len(exp_trajectories)),
                min(len(exp_trajectories), 1000),
                replace=False,
            )
            rest_indexes = [
                i for i in range(len(exp_trajectories)) if i not in selected_indexes
            ]
            rest_trajectories = [
                x for i, x in enumerate(exp_trajectories) if i in rest_indexes
            ]

            for trajectory in rest_trajectories:
                correlation_trajectories.append(trajectory)

            exp_trajectories = [
                x for i, x in enumerate(exp_trajectories) if i in selected_indexes
            ]

            with open(
                Path(out_path, "correlation_trajectories_{}.dat".format(index)), "w"
            ) as f:
                json.dump(correlation_trajectories, f)

            exp_trajectories = list(
                map(lambda x: TrajectoryUtil.point_to_cell(x), exp_trajectories)
            )
            with open(
                Path(
                    Configuration.CLEANSED_DATA_PATH.format(dataset.value),
                    "exp_trajectories_{}.dat".format(index),
                ),
                "w",
            ) as f:
                json.dump(exp_trajectories, f)
        print("Generation OK.")
