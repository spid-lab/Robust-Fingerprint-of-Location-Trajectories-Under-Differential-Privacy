from imports import *
from configuration import *
from dataset import *
from fingerprinting import *
from detection import *
from sampling import *
from attack import *

class Evaluation:


    @staticmethod
    def evaluate_detection_accuracy(data, trial_rep_count, sub_trial_rep_count, trajectory_count, party_count, trajectory_length, fp_ratio, attack, correlation_model, tau = Configuration.TAU, theta = Configuration.THETA, attack_ratio = 0.8, collusion_count = 3, p_estimate = None, debug = False, parallel = False):

        def single_trial(trial_index, sub_trial_rep_count, data, trajectory_count, party_count, fp_ratio, attack, correlation_model, tau, theta, attack_ratio, collusion_count, p_estimate, debug):
            if debug: print("Trial # {}".format(trial_index))
            selected_trajectories = Sampling.sample_count(data, trajectory_count)

            copies = [[] for _ in range(party_count)]
            aux_info = []
            for trajectory_id, selected_trajectory in enumerate(selected_trajectories):
                selected_trajectory = selected_trajectory[:trajectory_length]

                if debug: print("Generating fingerprinted copies.")

                for party_index in range(party_count):
                    copies[party_index].append(Fingerprinting.probabilistic_fingerprint(selected_trajectory, tau, fp_ratio, theta, correlation_model, debug=False))


            results = np.zeros(sub_trial_rep_count)
            if debug: print("Performing attack...")
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
                            leak_trajectory = Attack.probabilistic_collusion_attack(victim_trajectories, p_estimate, tau, correlation_model, attack_ratio = attack_ratio)


                    if debug: print("Detecting...")
                    sus, scores = Detection.similarity_detection(leak_trajectory, [copies[party_index][trajectory_idx] for party_index in range(party_count)])


                    sus_list.append(sus)
                results[sub_trial_index] =  1 if max(set(sus_list), key=sus_list.count) in leak_party_indexes else 0
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
        count = 0
        for trajectory in dataset:
            for idx, point in enumerate(trajectory):
                x, y = point[0], point[1]
                if (x, y) == tuple(pattern[0]):
                    for pattern_id, cell in enumerate(pattern):
                        if not pattern_id: continue
                        if idx + pattern_id < len(trajectory) and tuple(cell) == tuple((trajectory[idx+pattern_id][0], trajectory[idx+pattern_id][1])):
                            continue
                        else:
                            break
                    else:
                        count += 1

        return count

    @staticmethod
    def eval_area_query_answering(orig_dataset, eval_dataset, grid_size = None, query_rep_count = Configuration.QUERY_REP_COUNT):
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
            # print(sampled_center, sampled_radius, orig_count, fp_count)
            errors[query_id] = abs(orig_count - fp_count) / max(1, orig_count)
        return np.mean(errors)




    @staticmethod
    def eval_pattern_query_answering(orig_dataset, eval_dataset, transition, gram = 2, grid_size = None, query_rep_count = Configuration.QUERY_REP_COUNT):
        if grid_size:
            orig_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), orig_dataset))
            eval_dataset = list(map(lambda x: TrajectoryUtil.project_trajectory_to_grid(x, grid_size), eval_dataset))
            new_transition = defaultdict(lambda : defaultdict(lambda: 0))
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
            # print(sampled_pattern, orig_count, fp_count)
            errors[query_id] = abs(orig_count - fp_count) / max(1, orig_count)
        return np.mean(errors)



    @staticmethod
    def eval_popularity(orig_dataset, eval_dataset, grid_size = None):
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
            return sorted(counter.keys(), key = lambda x: -counter[x])



        orig_popularity = count_popularity(orig_dataset)
        eval_popularity = count_popularity(eval_dataset)

        orig_rank = get_rank(orig_popularity, grid_size)
        eval_rank = get_rank(eval_popularity, grid_size)
        return kendalltau(orig_rank, eval_rank)[0]


    @staticmethod
    def eval_trip_error(orig_dataset, eval_dataset, grid_size = None, bin_count = 10):
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
    def eval_diameter_error(orig_dataset, eval_dataset, grid_size = None, bin_count = 10):
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
        orig_trajectories = [[(point[0], point[1]) for point in orig_trajectory] for orig_trajectory in orig_dataset]
        eval_trajectories = [[(point[0], point[1]) for point in eval_trajectory] for eval_trajectory in eval_dataset]
        results = Parallel(n_jobs=16)(delayed(dtw_ndim.distance)(np.array(orig_trajectory), np.array(eval_trajectory)) for orig_trajectory, eval_trajectory in zip(orig_trajectories, eval_trajectories))
        return np.mean(results)