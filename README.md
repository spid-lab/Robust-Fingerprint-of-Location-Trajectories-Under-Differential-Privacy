# Robust-Fingerprint-of-Location-Trajectories-Under-Differential-Privacy

This repository contains the source code for the paper titled "Robust Fingerprint of Location Trajectories Under Differential Privacy" (PoPETs 23).

## Prerequisites

- Python 3.10
- Packages listed in `requirements.txt`

## Installation

To set up the required environment, follow these steps:

1. Install Python 3.10 from the official Python website: https://www.python.org/downloads/

2. Clone this repository to your local machine.

3. Open a terminal or command prompt and navigate to the project directory.

4. Install the necessary packages by running the following command: `pip install -r requirements.txt`.

## Datasets

In general, place your downloaded/generated datasets in the `data/{dataset_name}/raw/`. Make sure to replace `{dataset_name}` with the appropriate name of your dataset.

### The GeoLife dataset
- Download `Geolife Trajectories 1.3.zip` from [GeoLife GPS Trajectory Dataset](https://www.microsoft.com/en-us/download/details.aspx?id=52367)
- Extract the compressed file to data/geo_life/raw/

### The Taxi dataset
- Download `Porto_taxi_data_test_partial_trajectories.csv` from [Taxi Service Trajectory - Prediction Challenge, ECML PKDD](https://data.world/uci/taxi-service-trajectory-prediction-challenge-ecml-pkdd)
- Place the `Porto_taxi_data_test_partial_trajectories.csv` file in /data/taxi/raw/ and rename it as `data.csv`.

### The Brinkhoff datasets (OldenBurg and San Joaquin)
- Download the generator from [Network-based Generator of Moving Objects](https://iapg.jade-hs.de/personen/brinkhoff/generator)
- Follow the instructions on the web page to generate moving objects using the Brinkhoff generator.
- The generator will output a `.dat` file. Place the file in /data/{dataset_name/raw/ and rename it as `raw_trajectories.dat`.
- A dump can be found: [Here](https://drive.google.com/file/d/1oDXU4PIsOayQtcVqJDObFSqoMhsVijt-/view?usp=sharing)


## Running the Code

To run the code with the provided demo evaluation, follow these steps:

1. Open a terminal or command prompt and navigate to the project directory.

2. Run the following command: `python main.py`. It contains a evaluation demo as well.

## Parameters in evaluation

### Detection accuracy

- `data`: The DP dataset to be evaluated. It should be loaded using `DataLoader.load_dp_data()`.
- `trial_rep_count`: The number of FP datasets generated during evaluation.
- `sub_trial_rep_count`: The number of single experiments on each FP dataset, so the overall trial number is `trial_rep_count * sub_trial_rep_count`.
- `trajectory_count`: The number of trajectories that are exposed in the leaked dataset.
- `party_count`: The number of copies for each trajectory, i.e., the number of analyzers.
- `trajectory_length`: The maximum length of each trajectory.
- `fp_ratio`: The predefined fingerprinting ratio. `fp_ratio = 0.3` means ~30% points will be fingerprinted (distorted), but due to post-processing, the number of distorted point might be larger.
- `attack`: The attack method. Can be one of `Attack.random_distortion_attack`, `Attack.correlation_attack`, `Attack.majority_collusion_attack`, `Attack.probabilistic_collusion_attack`. Details can be found in the paper.
- `correlation_model`： The correlation model from `Correlation()`.
- `tau`: The correlation threshold used for fingerprinting. Don't modify this unless necessary.
- `theta`: The fingerprint balancing factor used for fingerprinting. Don't modify this unless necessary.
- `attack_ratio`: The attack ratio. For random flipping attacks, correlation-based flipping attacks, and probabilistic collusion attacks, it represents the probability of a point being distorted. For majority collusion attacks, it has no effect.
- `collusion_count`: The number of analyzers that will collude in the two collusion attacks. It has no effect in the two flipping attacks.
- `p_estimate`: The estimated fingerprinting ratio by the analyzer(s) used in probabilistic collusion attacks, and it has no effect in the rest of the attacks.
- `debug`: Debug flag. Set it to False.
- `parallel`: Parallel flag that shows whether the evaluation will be executed using multiprocessing (very time and space consuming!).

### Utility evaluation
- `orig_dataset`: The original dataset.
- `dp_dataset`: The generated DP dataset (not fingerprinted yet).
- `utility_metric`: The utility metric. Can be one of `EvaluationMetric.QA_POINTS`, `EvaluationMetric.QA_PATTERNS`, `EvaluationMetric.AREA_POPULARITY`, `EvaluationMetric.TRIP_ERROR`, `EvaluationMetric.DIAMETER_ERROR`, and `EvaluationMetric.TRIP_SIMILARITY`. Details can be found in the paper.
- `fp_ratio`: The predefined fingerprinting ratio. `fp_ratio = 0.3` means ~30% points will be fingerprinted (distorted), but due to post-processing, the number of distorted point might be larger.
- `tau`: The correlation threshold used for fingerprinting. Don't modify this unless necessary.
- `theta`: The fingerprint balancing factor used for fingerprinting. Don't modify this unless necessary.
- `correlation_model`： The correlation model from `Correlation()`.
- `debug`: Debug flag. Set it to False.