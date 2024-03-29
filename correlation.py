from imports import *
from configuration import *
from coordinates import *
from distance import *


class Correlation:
    """
    A class for computing correlation-based transition and emission probabilities.
    """

    def __init__(self, prior_knowledge):
        """
        Initializes the Correlation class with prior knowledge.

        Args:
            prior_knowledge (list): Prior knowledge of cell trajectories.
        """

        def generate_correlation_model(prior):
            emission = defaultdict(lambda: 0)
            transition = defaultdict(lambda: defaultdict(lambda: 0))

            for cell_trajectory in prior:
                for prev_point, curr_point in zip(cell_trajectory, cell_trajectory[1:]):
                    transition[Coordinates.get_cell(prev_point)][
                        Coordinates.get_cell(curr_point)
                    ] += 1
                    emission[Coordinates.get_cell(curr_point)] += 1

            return emission, transition

        self.emission, self.transition = generate_correlation_model(prior_knowledge)

    def get_transition(self, prior):
        """
        Computes the transition probabilities from the prior cell.

        Args:
            prior (tuple): The prior cell as a tuple (x, y).

        Returns:
            dict: The transition probabilities to neighboring cells.
        """
        local_transition = {}
        x, y = prior[0], prior[1]

        total_transition = sum(self.transition[(x, y)].values())

        if total_transition <= 0:
            for x_cell in range(
                x - Configuration.NEIGHBOR_RANGE, x + Configuration.NEIGHBOR_RANGE + 1
            ):
                for y_cell in range(
                    y - Configuration.NEIGHBOR_RANGE,
                    y + Configuration.NEIGHBOR_RANGE + 1,
                ):
                    if Coordinates.in_range_cell((x_cell, y_cell)):
                        local_transition[(x_cell, y_cell)] = 1

            return {key: 1 / len(local_transition) for key in local_transition.keys()}
        else:
            return {
                key: value / total_transition
                for key, value in self.transition[(x, y)].items()
            }

    def get_vanilla_transition(self, prior):
        """
        Retrieves the original (non-normalized) transition probabilities from the prior cell.

        Args:
            prior (tuple): The prior cell as a tuple (x, y).

        Returns:
            dict: The original transition probabilities to neighboring cells.
        """
        x, y = prior[0], prior[1]
        return self.transition[(x, y)]

    def get_emission(self, prior):
        """
        Computes the emission probabilities from the prior cell.

        Args:
            prior (tuple): The prior cell as a tuple (x, y).

        Returns:
            dict: The emission probabilities to neighboring cells.
        """
        local_emission = {}
        x, y = prior[0], prior[1]

        for x_cell in range(
            x - Configuration.NEIGHBOR_RANGE, x + Configuration.NEIGHBOR_RANGE + 1
        ):
            for y_cell in range(
                y - Configuration.NEIGHBOR_RANGE, y + Configuration.NEIGHBOR_RANGE + 1
            ):
                if Coordinates.in_range_cell((x_cell, y_cell)):
                    local_emission[(x_cell, y_cell)] = self.emission[(x_cell, y_cell)]

        total_emission = sum(local_emission.values())

        if total_emission <= 0:
            return {key: 1 / len(local_emission) for key in local_emission.keys()}
        else:
            return {
                key: value / total_emission for key, value in local_emission.items()
            }

    def get_all_transition(self, prev_point, true_point, tau, consider_distance=True):
        """
        Computes all possible transitions from the previous point.

        Args:
            prev_point (tuple): The previous point as a tuple (x, y).
            true_point (tuple): The true point as a tuple (x, y).
            tau (float): The correlation threshold.
            consider_distance (bool): Whether to consider the distance threshold (default: True).

        Returns:
            tuple: The transition dictionaries (candidates, tau_candidates, tau_dist_candidates).
        """
        candidates = self.get_transition(prev_point)
        tau_candidates = dict(filter(lambda x: x[1] >= tau, candidates.items()))

        if consider_distance:
            dist = Distance.sq_euclidean(prev_point, true_point)
            tau_dist_candidates = dict(
                filter(
                    lambda x: Distance.sq_euclidean(x[0], true_point) <= dist,
                    tau_candidates.items(),
                )
            )
            return candidates, tau_candidates, tau_dist_candidates
        else:
            return candidates, tau_candidates
