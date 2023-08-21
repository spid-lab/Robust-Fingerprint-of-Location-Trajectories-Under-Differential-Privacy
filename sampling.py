from imports import *
from configuration import *
from distance import *
from coordinates import *


class Sampling:
    """
    Provides various sampling methods for trajectory data.
    """

    @staticmethod
    def sample_proportionally_with_truth(candidates, truth, p):
        if sum(candidates.values()) <= 0:
            sampled_cell = list(candidates.keys())[random.randint(len(candidates))]
        else:
            if truth:
                total = sum(candidates.values()) - candidates[truth]
                if total:
                    candidates = {
                        key: p * value / total for key, value in candidates.items()
                    }
                    candidates[truth] = 1 - p
                else:
                    candidates[truth] = 1
            else:
                total = sum(candidates.values())
                candidates = {key: value / total for key, value in candidates.items()}
            sampled_cell = list(candidates.keys())[
                random.choice(
                    range(len(candidates)),
                    p=[candidates[key] for key in candidates.keys()],
                )
            ]

        fp_state = 0 if truth == sampled_cell else 1

        return sampled_cell, fp_state

    @staticmethod
    def sample_closest(cell, candidates):
        closest_pt = None, None
        min_dist = None
        for cand in candidates:
            dist = Distance.sq_euclidean(cell, cand)
            if min_dist == None or dist < min_dist:
                min_dist = dist
                closest_pt = cand
        return closest_pt

    @staticmethod
    def sample_candidates_vanilla(
        prev_cell, true_cell, p, tau, correlation, replace=True, debug=False
    ):
        candidates = correlation.get_transition(prev_cell)
        filtered_candidates = dict(filter(lambda x: x[1] >= tau, candidates.items()))

        if len(filtered_candidates) == 0:
            sampled_cell, fp_state = true_cell, 0
        elif true_cell not in filtered_candidates.keys():
            sampled_cell, fp_state = Sampling.sample_proportionally_with_truth(
                filtered_candidates, None, None
            )
        else:
            if filtered_candidates[true_cell] == sum(filtered_candidates.values()):
                sampled_cell = Sampling.sample_nearby_point(
                    true_cell, Configuration.SCALE
                )
                fp_state = 1
            else:
                sampled_cell, fp_state = Sampling.sample_proportionally_with_truth(
                    filtered_candidates, true_cell, p
                )
        return sampled_cell, fp_state

    @staticmethod
    def sample_candidates(
        prev_cell, true_cell, p, tau, correlation=None, replace=True, debug=False
    ):
        (
            candidates,
            tau_candidates,
            tau_dist_candidates,
        ) = correlation.get_all_transition(
            prev_cell, true_cell, tau, consider_distance=True
        )

        fp_state = 0

        if true_cell in tau_dist_candidates.keys():
            if len(tau_dist_candidates) > 1:
                sampled_cell, fp_state = Sampling.sample_proportionally_with_truth(
                    tau_dist_candidates, true_cell, p
                )
            elif len(tau_candidates) > 1:
                sampled_cell, fp_state = Sampling.sample_proportionally_with_truth(
                    tau_candidates, true_cell, p
                )
            else:
                sampled_cell, fp_state = true_cell, 0
        else:
            if len(tau_candidates) > 1:
                if replace:
                    temp_true_cell = Sampling.sample_closest(true_cell, tau_candidates)
                    if Distance.sq_euclidean(
                        temp_true_cell, true_cell
                    ) < Distance.sq_euclidean(prev_cell, true_cell):
                        sampled_cell, _ = Sampling.sample_proportionally_with_truth(
                            tau_candidates, temp_true_cell, p
                        )
                        fp_state = 1
                    else:
                        sampled_cell, fp_state = true_cell, 0
                else:
                    sampled_cell, _ = Sampling.sample_proportionally_with_truth(
                        tau_candidates, None, None
                    )
                    fp_state = 1
            else:
                sampled_cell, fp_state = true_cell, 0
        return sampled_cell, fp_state

    @staticmethod
    def sample_uniformly(poly):
        min_x, min_y, max_x, max_y = poly.bounds
        while True:
            p = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if poly.contains(p):
                return p.x, p.y

    @staticmethod
    def sample_coordinate(cell):
        assert Coordinates.in_range_cell(cell)
        x, y = cell
        sampled_x = random.uniform(x, x + 1)
        sampled_y = random.uniform(y, y + 1)

        return Coordinates.get_coordinate((sampled_x, sampled_y))

    @staticmethod
    def sample_alter_points(points, scale):
        alter_points = []
        for point in points:
            while True:
                new_lat, new_lng = Sampling.sample_nearby_point(point, scale)
                if Coordinates.in_range_cell((new_lat, new_lng)):
                    break
            alter_points.append((new_lat, new_lng))
        return alter_points

    @staticmethod
    def sample_nearby_point(point, scale):
        lat, lng = point
        while True:
            new_lat = int(lat + random.uniform(-scale, scale + 1))
            new_lng = int(lng + random.uniform(-scale, scale + 1))
            if new_lat != lat or new_lng != lng:
                break
        return new_lat, new_lng

    @staticmethod
    def sample_portion(candidates, portion):
        count = int(portion * len(candidates))
        return Sampling.sample_count(candidates, count)

    @staticmethod
    def sample_count(candidates, count):
        if type(candidates) == int:
            return random.choice(
                range(candidates), max(1, count), replace=False
            ).tolist()
        else:
            indexes = random.choice(
                range(len(candidates)), max(1, count), replace=False
            )
            return [candidates[index] for index in indexes]
