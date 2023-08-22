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
