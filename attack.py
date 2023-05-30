from imports import *
from configuration import *
from sampling import *

class Attack:

    @staticmethod
    def random_distortion_attack(leak_trajectory, ratio):

        new_trajectory = []
        for lat, lng, tt in leak_trajectory:
            if random.random() < ratio:
                sampled_lat, sampled_lng = Sampling.sample_nearby_point((lat, lng), 1)
                new_trajectory.append((sampled_lat, sampled_lng, tt))
            else:
                new_trajectory.append((lat, lng, tt))
        return new_trajectory

    @staticmethod
    def correlation_attack(leak_trajectory, tau, ratio, correlation, replace = True, debug = False):
        # flp = 0
        new_trajectory = []
        first_lat, first_lng, first_time = leak_trajectory[0]
        new_trajectory.append((first_lat, first_lng, first_time))
        prev_lat, prev_lng = first_lat, first_lng
        for i, ((lat, lng, _), (current_lat, current_lng, current_time)) in enumerate(zip(leak_trajectory, leak_trajectory[1:])):
            candidates, tau_candidates = correlation.get_all_transition((prev_lat, prev_lng), None, tau, False)
            sampled_lat, sampled_lng = current_lat, current_lng

            if (current_lat, current_lng) not in tau_candidates.keys():
                if random.random() < ratio:
                    if len(candidates) > 0:
                        if len(tau_candidates) > 0:
                            sampled_lat, sampled_lng = max(tau_candidates.keys(), key=lambda x: tau_candidates[x])
                        else:
                            sampled_lat, sampled_lng = max(candidates.keys(), key=lambda x: candidates[x])
                        if debug: print(i, "Not in, Flip", current_lat, current_lng, "->",  sampled_lat, sampled_lng)

                    else:
                        if debug: print("No candidate, pass")

                # flp += 1
            #            print(current_lat, current_lng, lat_cell, lng_cell)
            elif random.random() < ratio:
                sampled_lat, sampled_lng = Sampling.sample_nearby_point((current_lat, current_lng), Configuration.SCALE)

                if debug: print(i, "in, Flip", current_lat, current_lng, "->",  sampled_lat, sampled_lng)
            new_trajectory.append((sampled_lat, sampled_lng, current_time))

            if replace:
                prev_lat, prev_lng = sampled_lat, sampled_lng
            else:
                prev_lat, prev_lng = current_lat, current_lng
        return new_trajectory

    @staticmethod
    def majority_collusion_attack(colluding_trajectories):
        leak_trajectory = []
        #   print("Len: ", len(leaked_trajectories))
        for i in range(len(colluding_trajectories[0])):
            #      print(i)
            count_dict = defaultdict(lambda: 0)
            for colluding_trajectory in colluding_trajectories:
                cell_lat, cell_lng, true_time = colluding_trajectory[i]
                count_dict[(cell_lat, cell_lng)] += 1
            #      print (count_dict)
            max_ct = max(count_dict.values())
            max_candidates = []
            for key, ct in count_dict.items():
                if max_ct == ct:
                    max_candidates.append(key)
            max_key = max_candidates[random.choice(range(len(max_candidates)))]
            leak_trajectory.append((max_key[0], max_key[1], true_time))
        return leak_trajectory



    def probabilistic_collusion_attack(colluding_trajectories, p_estimate, tau, correlation, attack_ratio = 1, debug= False):
        leaked_count = len(colluding_trajectories)
        leak_trajectory = []
        # Process the first entry
        count_dict = defaultdict(lambda: 0)
        for colluding_trajectory in colluding_trajectories:
            cell_lat, cell_lng, true_time = colluding_trajectory[0]
            count_dict[(cell_lat, cell_lng)] += 1
        for key, count in count_dict.items():
            count_dict[key] = (1 - p_estimate)** count * p_estimate ** (leaked_count - count)
        (cell_lat, cell_lng), _ = Sampling.sample_proportionally_with_truth(count_dict, None, None)
        leak_trajectory.append((cell_lat, cell_lng, true_time))

        # Process the rest sample
        for i in range(len(colluding_trajectories[0])):

            if i == 0: continue

            if debug: print(i, leak_trajectory[-1])

            prev_lat, prev_lng, prev_time = leak_trajectory[-1]
            count_dict = defaultdict(lambda: 0)
            for colluding_trajectory in colluding_trajectories:
                cell_lat, cell_lng, time = colluding_trajectory[i]
                count_dict[(cell_lat, cell_lng)] += 1
            if debug: print ("Count:",count_dict)


            if random.random() < attack_ratio:
                roll_dict = {}
                for key, count in count_dict.items():
                    #         print(key, prev_lat, prev_lng)
                    transition = correlation.get_transition((prev_lat, prev_lng))
                    if key in transition.keys() and transition[key] > tau:
                        tran_prob = transition[key]
                    else:
                        tran_prob = 0
                    if tran_prob > 0:
                        roll_dict[key] = tran_prob * (1 - p_estimate)** count * p_estimate ** (leaked_count - count)
                if debug: print(roll_dict)
                if len(roll_dict) > 0:
                    if debug: print("Sample among truths")
                    (cell_lat, cell_lng), _ = Sampling.sample_proportionally_with_truth(roll_dict, None, None)
                else:
                    if debug: print("Pick MAX Prob")
                    transition = correlation.get_transition((prev_lat, prev_lng))
                    cell_lat, cell_lng = sorted(transition.keys(), key = lambda x: -transition[x])[0]
            else:
                if debug: print("Pick as MJR")
                cell_lat, cell_lng = sorted(count_dict.keys(), key = lambda x: -count_dict[x])[0]

            if debug: print("Report:", cell_lat, cell_lng)
            leak_trajectory.append((cell_lat, cell_lng, true_time))

        return leak_trajectory
