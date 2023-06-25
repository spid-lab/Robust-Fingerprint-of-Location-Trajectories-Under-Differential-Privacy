from imports import *
from configuration import *
from dataset import *
from fingerprinting import *
from detection import *
from sampling import *
from attack import *
from trajectory_util import *

class Evaluation:
    """
    A class for evaluating privacy-preserving techniques.
    """

    @staticmethod
    def generate_sample_dataset(selected_trajectory, party_count, fp_ratio, tau, theta, correlation, debug=False):
        """
        Generates sample datasets by applying a fingerprinting method to a selected trajectory.

        Args:
            selected_trajectory (list): Selected trajectory data.
            party_count (int): Number of copies to generate.
            fp_ratio (float): False positive ratio.
            tau (float): Correlation threshold.
            theta (float): Balancing factor.
            correlation (object): Correlation model.
            debug (bool): Debug flag.

        Returns:
            list: Generated copies of the selected trajectory.
        """
        copies = []
        if debug: print("Generating fingerprinted copies.")
        for _ in range(party_count):
            copies.append(Fingerprinting.probabilistic_fingerprint(selected_trajectory, tau, fp_ratio, theta, correlation, debug=False))
        return copies

    @staticmethod
    def evaluate_detection_accuracy(data, trial_rep_count, sub_trial_rep_count, trajectory_count, party_count, trajectory_length, fp_ratio, attack, correlation_model, tau=Configuration.TAU, theta=Configuration.THETA, attack_ratio=0.8, collusion_count=3, p_estimate=None, debug=False, parallel=False):
        """
        Evaluate the detection accuracy of a privacy-preserving technique.

        Args:
            data (list): The dataset.
            trial_rep_count (int): The number of trial repetitions.
            sub_trial_rep_count (int): The number of sub-trial repetitions.
            trajectory_count (int): The number of trajectories.
            party_count (int): The number of parties.
            trajectory_length (int): The length of trajectories.
            fp_ratio (float): The fingerprinting ratio.
            attack (Attack): The attack type.
            correlation_model (object): The correlation model.
            tau (float, optional): The threshold for similarity detection. Defaults to Configuration.TAU.
            theta (float, optional): The threshold for probabilistic fingerprinting. Defaults to Configuration.THETA.
            attack_ratio (float, optional): The attack ratio. Defaults to 0.8.
            collusion_count (int, optional): The number of colluding parties. Defaults to 3.
            p_estimate (float, optional): The probability estimate for probabilistic collusion attack. Defaults to None.
            debug (bool, optional): Enable debug mode. Defaults to False.
            parallel (bool, optional): Enable parallel execution. Defaults to False.

        Returns:
            float: The average detection accuracy.
        """

        def single_trial(trial_index, sub_trial_rep_count, data, trajectory_count, party_count, fp_ratio, attack, correlation_model, tau, theta, attack_ratio, collusion_count, p_estimate, debug):
            if debug:
                print("Trial # {}".format(trial_index))
            selected_trajectories = Sampling.sample_count(data, trajectory_count)

            copies = [[] for _ in range(party_count)]
            aux_info = []
            for trajectory_id, selected_trajectory in enumerate(selected_trajectories):
                selected_trajectory = selected_trajectory[:trajectory_length]

                if debug:
                    print("Generating fingerprinted copies.")

                for party_index in range(party_count):
                    copies[party_index].append(Fingerprinting.probabilistic_fingerprint(selected_trajectory, tau, fp_ratio, theta, correlation_model, debug=False))

            results = np.zeros(sub_trial_rep_count)
            if debug:
                print("Performing attack...")
            for sub_trial_index in range(sub_trial_rep_count):
                if attack == Attack.correlation_attack or attack == Attack.random_distortion_attack:
                    assert attack_ratio
                    leak_party_indexes = Sampling.sample_count(party_count, 1)
                else:
                    assert collusion_count > 1
                    leak_party_indexes = Sampling.sample_count(party_count, collusion_count)

                sus_list = []

                for trajectory_idx in range(trajectory_count):
                    if attack == Attack.random_distortion_attack:
                        victim_trajectory = copies[leak_party_indexes[0]][trajectory_idx][0]
                        leak_trajectory = Attack.random_distortion_attack(victim_trajectory, attack_ratio)
                    if attack == Attack.correlation_attack:
                        victim_trajectory = copies[leak_party_indexes[0]][trajectory_idx][0]
                        leak_trajectory = Attack.correlation_attack(victim_trajectory, tau, attack_ratio, correlation_model)
                    else:
                        victim_trajectories = [copies[party_index][trajectory_idx][0] for party_index in leak_party_indexes]
                        if attack == Attack.majority_collusion_attack:
                            leak_trajectory = Attack.majority_collusion_attack(victim_trajectories)
                        elif attack == Attack.probabilistic_collusion_attack:
                            assert p_estimate
                            leak_trajectory = Attack.probabilistic_collusion_attack(victim_trajectories, p_estimate, tau, correlation_model, attack_ratio=attack_ratio)

                    if debug:
                        print("Detecting...")
                    sus, scores = Detection.similarity_detection(leak_trajectory, [copies[party_index][trajectory_idx] for party_index in range(party_count)])
                    sus_list.append(sus)
                results[sub_trial_index] = 1 if max(set(sus_list), key=sus_list.count) in leak_party_indexes else 0
            return np.mean(results)

        if parallel:
            results = Parallel(n_jobs=16)(delayed(single_trial)(trial_index, sub_trial_rep_count, data, trajectory_count, party_count, fp_ratio, attack, correlation_model, tau, theta, attack_ratio, collusion_count, p_estimate, debug) for trial_index in range(trial_rep_count))
        else:
            results = []
            for trial_index in range(trial_rep_count):
                results.append(single_trial(trial_index, sub_trial_rep_count, data, trajectory_count, party_count, fp_ratio, attack, correlation_model, tau, theta, attack_ratio, collusion_count, p_estimate, debug))
        return np.mean(results)

    @staticmethod
    def count_in_range(dataset, center, radius):
        """
        Count the number of points within a given range in a dataset.

        Args:
            dataset (list): The dataset.
            center (tuple): The center point as a tuple (x, y).
            radius (float): The radius of the range.

        Returns:
            int: The count of points within the range.
        """
        count = 0
        sq_radius = radius ** 2
        for trajectory in dataset:
            for point in trajectory:
                x, y = point[0], point[1]
                if Distance.sq_euclidean((x, y), center) < sq_radius:
                    count += 1
        return count

    @staticmethod
    def count_pattern_in_range(dataset, pattern):
        """
        Count the occurrences of a pattern within a range in a dataset.

        Args:
            dataset (list): The dataset.
            pattern (list): The pattern as a list of cells.

        Returns:
            int: The count of pattern occurrences within the range.
        """
        count = 0
        for trajectory in dataset:
            for idx, point in enumerate(trajectory):
                x, y = point[0], point[1]
                if (x, y) == tuple(pattern[0]):
                    for pattern_id, cell in enumerate(pattern):
                        if not pattern_id:
                            continue
                        if idx + pattern_id < len(trajectory) and tuple(cell) == tuple((trajectory[idx + pattern_id][0], trajectory[idx + pattern_id][1])):
                            continue
                        else:
                            break
                    else:
                        count += 1
        return count

    @staticmethod
    def eval_area_query_answering(orig_dataset, eval_dataset, grid_size=None, query_rep_count=Configuration.QUERY_REP_COUNT):
        """
        Evaluate the error in area query answering.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.
            grid_size (int, optional): The grid size. Defaults to None.
            query_rep_count (int, optional): The number of query repetitions. Defaults to Configuration.QUERY_REP_COUNT.

        Returns:
            float: The average error in area query answering.
        """
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
        else:
            grid_size = Configuration.GRID_SIZE

        errors = np.zeros((query_rep_count))
        for query_id in range(query_rep_count):
            sampled_center = random.randint(0, grid_size, 2)
            sampled_radius = random.randint(0, grid_size)
            orig_count = Evaluation.count_in_range(orig_dataset, sampled_center, sampled_radius)
            fp_count = Evaluation.count_in_range(eval_dataset, sampled_center, sampled_radius)
            errors[query_id] = abs(orig_count - fp_count) / max(1, orig_count)
        return np.mean(errors)

    @staticmethod
    def eval_pattern_query_answering(orig_dataset, eval_dataset, transition, gram=2, grid_size=None, query_rep_count=Configuration.QUERY_REP_COUNT):
        """
        Evaluate the error in pattern query answering.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.
            transition (dict): The transition probabilities.
            gram (int, optional): The pattern gram. Defaults to 2.
            grid_size (int, optional): The grid size. Defaults to None.
            query_rep_count (int, optional): The number of query repetitions. Defaults to Configuration.QUERY_REP_COUNT.

        Returns:
            float: The average error in pattern query answering.
        """
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
            new_transition = defaultdict(lambda: defaultdict(lambda: 0))
            for tran_from in transition.keys():
                new_tran_from = TrajectoryUtil.project_cell_to_grid(tran_from[0], tran_from[1], grid_size)
                for tran_to in transition[tran_from].keys():
                    new_tran_to = TrajectoryUtil.project_cell_to_grid(tran_to[0], tran_to[1], grid_size)
                    new_transition[new_tran_from][new_tran_to] += transition[tran_from][tran_to]
            transition = new_transition
        else:
            grid_size = Configuration.GRID_SIZE

        errors = np.zeros((query_rep_count))
        for query_id in range(query_rep_count):
            sampled_pattern = []
            while len(sampled_pattern) < gram:
                for cell_idx in range(gram):
                    if not cell_idx:
                        sampled_pattern.append(list(transition.keys())[random.choice(len(transition.keys()))])
                    else:
                        next_transition = transition[tuple(sampled_pattern[-1])]
                        if next_transition:
                            sampled_pattern.append(list(next_transition.keys())[random.choice(len(next_transition.keys()))])
                        else:
                            sampled_pattern = []
                            break

            orig_count = Evaluation.count_pattern_in_range(orig_dataset, sampled_pattern)
            fp_count = Evaluation.count_pattern_in_range(eval_dataset, sampled_pattern)
            errors[query_id] = abs(orig_count - fp_count) / max(1, orig_count)
        return np.mean(errors)

    @staticmethod
    def eval_popularity(orig_dataset, eval_dataset, grid_size=None):
        """
        Evaluate the popularity similarity between datasets.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.
            grid_size (int, optional): The grid size. Defaults to None.

        Returns:
            float: The Kendall's tau rank correlation coefficient.
        """
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
        else:
            grid_size = Configuration.GRID_SIZE

        def get_rank(counter, grid_size):
            ranking = [grid_size * grid_size - 1 for _ in range(grid_size * grid_size)]
            for rank, cell in enumerate(counter):
                ranking[cell[0] * grid_size + cell[1]] = rank
            return ranking

        def count_popularity(dataset):
            counter = defaultdict(lambda: 0)
            for trajectory in dataset:
                for point in trajectory:
                    counter[(point[0], point[1])] += 1
            return sorted(counter.keys(), key=lambda x: -counter[x])

        orig_popularity = count_popularity(orig_dataset)
        eval_popularity = count_popularity(eval_dataset)

        orig_rank = get_rank(orig_popularity, grid_size)
        eval_rank = get_rank(eval_popularity, grid_size)
        return kendalltau(orig_rank, eval_rank)[0]

    @staticmethod
    def eval_trip_error(orig_dataset, eval_dataset, grid_size=None, bin_count=10):
        """
        Evaluate the error in trip length distribution.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.
            grid_size (int, optional): The grid size. Defaults to None.
            bin_count (int, optional): The number of bins for histogram calculation. Defaults to 10.

        Returns:
            float: The Jensen-Shannon divergence between the trip length distributions.
        """
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
        else:
            grid_size = Configuration.GRID_SIZE

        orig_lengths = [TrajectoryUtil.calc_trajectory_length(trajectory) for trajectory in orig_dataset]
        eval_lengths = [TrajectoryUtil.calc_trajectory_length(trajectory) for trajectory in eval_dataset]

        max_distance = max(orig_lengths)
        bins = np.concatenate([np.linspace(0, max_distance, bin_count), [math.inf]])
        return Distance.jsd(np.histogram(orig_lengths, bins)[0], np.histogram(eval_lengths, bins)[0])

    @staticmethod
    def eval_diameter_error(orig_dataset, eval_dataset, grid_size=None, bin_count=10):
        """
        Evaluate the error in trajectory diameter distribution.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.
            grid_size (int, optional): The grid size. Defaults to None.
            bin_count (int, optional): The number of bins for histogram calculation. Defaults to 10.

        Returns:
            float: The Jensen-Shannon divergence between the trajectory diameter distributions.
        """
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
        else:
            grid_size = Configuration.GRID_SIZE

        orig_distances = []
        eval_distances = []
        max_distance = 0
        for trajectory in orig_dataset:
            for prev_point, curr_point in zip(trajectory, trajectory[1:]):
                distance = Distance.euclidean(prev_point, curr_point)
                orig_distances.append(distance)
                max_distance = max(max_distance, distance)
        for trajectory in eval_dataset:
            for prev_point, curr_point in zip(trajectory, trajectory[1:]):
                distance = Distance.euclidean(prev_point, curr_point)
                eval_distances.append(distance)
        bins = np.concatenate([np.linspace(0, max_distance, bin_count), [math.inf]])
        return Distance.jsd(np.histogram(orig_distances, bins)[0], np.histogram(eval_distances, bins)[0])

    @staticmethod
    def evaluate_dtw_distance(orig_dataset, eval_dataset):
        """
        Evaluate the DTW distance between datasets.

        Args:
            orig_dataset (list): The original dataset.
            eval_dataset (list): The evaluated dataset.

        Returns:
            float: The average DTW distance.
        """
        orig_trajectories = [[(point[0], point[1]) for point in orig_trajectory] for orig_trajectory in orig_dataset]
        eval_trajectories = [[(point[0], point[1]) for point in eval_trajectory] for eval_trajectory in eval_dataset]
        results = Parallel(n_jobs=16)(delayed(dtw_ndim.distance)(np.array(orig_trajectory), np.array(eval_trajectory)) for orig_trajectory, eval_trajectory in zip(orig_trajectories, eval_trajectories))
        return np.mean(results)
