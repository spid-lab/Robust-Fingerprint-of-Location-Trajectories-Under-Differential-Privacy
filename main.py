from imports import *
from dataset import *
from configuration import *
from data_loader import *
from dataset_util import *
from correlation import *
from privacy_metric import *
from evaluation import *


# Set dataset
dataset = Dataset.GEO_LIFE

# Generate cleansed datasets from raw data (5 copies)
DatasetUtil.generate_experimental_and_correlation_dataset(dataset)

index = 0   # use the first copy

# # # Generate correlation model
correlation_data = DataLoader.load_correlation_data(dataset, index)
correlation_model = Correlation(correlation_data)

# Load data
orig_data = DataLoader.load_experimental_data(dataset, index)

# Apply pim
PrivacyMetric.pim(orig_data[:100], dataset, epsilon=0.1, delta_dp=Configuration.DELTA_DP, correlation=correlation_model)

# Examples - evaluation
fp_ratio = 0.4
collusion_count = 3
attack_ratio = 0.8
party_count = 100
trajectory_length = 100
trial_rep_count = 10
sub_trial_rep_count = 200
trajectory_count = 1

exp_data = DataLoader.load_dp_data(dataset, epsilon = 0.9, method = 'pim', index = 0)

print("Accuracy: ", Evaluation.evaluate_detection_accuracy(
                        data = exp_data,
                        trial_rep_count = trial_rep_count,
                        sub_trial_rep_count = sub_trial_rep_count,
                        trajectory_count = trajectory_count,
                        party_count = party_count,
                        trajectory_length=trajectory_length,
                        fp_ratio = fp_ratio,
                        attack = Attack.correlation_attack,
                        correlation_model = correlation_model,
                        tau = Configuration.TAU,
                        theta = Configuration.THETA,
                        attack_ratio = attack_ratio,
                        collusion_count = collusion_count,
                        p_estimate = fp_ratio,
                        debug = False,
                        parallel = False))

# Experiment Name              | Expected Result  | Estimated Time
# ------------------------Accuracy-----------------------------
# Random Distortion            | 0.9995           | 27 seconds
# Correlation Distortion       | 0.9990           | 25 seconds
# Majority Collusion           | 1.0000           | 25 seconds
# Probabilistic Collusion      | 0.9995           | 27 seconds
# ------------------------Utility-----------------------------
# Query Answering (Points)     | 9.6892           | 85 seconds
# Query Answering (Patterns)   | 2.5377           | 19 seconds
# Area Popularity              | 0.6213           | 8  seconds
# Trip Error                   | 0.7484           | 8  seconds
# Diameter Error               | 0.1346           | 8 seconds

