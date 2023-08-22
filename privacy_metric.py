from imports import *
from configuration import *
from coordinates import *
from sampling import *


class PrivacyMetric:
    @staticmethod
    def pim(data, dataset, epsilon, delta_dp, correlation, copies=1):
        """
        Apply the PIM algorithm to generate differentially private copies of the input data.

        Args:
            data (list): The input trajectory data.
            dataset (Dataset): The dataset being used.
            epsilon (float): The privacy parameter.
            delta_dp (float): The delta parameter for differential privacy.
            correlation (Correlation): The correlation model for transition probabilities.
            copies (int, optional): The number of copies to generate. Defaults to 5.

        Returns:
            None
        """

        def apply_pim(trajectory, epsilon, delta_dp, correlation, length=100):
            prev_x, prev_y, prev_t = (
                int(trajectory[0][0]),
                int(trajectory[0][1]),
                trajectory[0][2],
            )

            posterior = np.zeros((Configuration.GRID_SIZE, Configuration.GRID_SIZE))
            posterior[prev_x][prev_y] = 1

            prior = np.zeros((Configuration.GRID_SIZE, Configuration.GRID_SIZE))
            for x in range(Configuration.GRID_SIZE):
                for y in range(Configuration.GRID_SIZE):
                    for (tran_x, tran_y), tran_prob in correlation.get_transition(
                        (x, y)
                    ).items():
                        prior[tran_x, tran_y] += posterior[x, y] * tran_prob

            result = [(prev_x, prev_y, prev_t)]
            for x_cell, y_cell, timestamp in trajectory[1:length]:
                true_x, true_y = x_cell, y_cell

                sorted_prior = []
                for x in range(Configuration.GRID_SIZE):
                    for y in range(Configuration.GRID_SIZE):
                        sorted_prior.append((-prior[x, y], x, y))
                heapq.heapify(sorted_prior)

                location_set = []
                set_sum = 0
                while True:
                    pr, x, y = heapq.heappop(sorted_prior)
                    if set_sum >= 1 - delta_dp:
                        break
                    location_set.append((x, y, -pr))
                    set_sum += -pr

                points = []
                for x, y, _ in location_set:
                    points += Coordinates.get_cell_corners((x, y))
                points = np.array(points)

                try:
                    c_hull = ConvexHull(points)
                except Exception as err:
                    points = [
                        (x, y)
                        for x, y in [
                            (
                                prev_x - Configuration.GRID_SIZE,
                                prev_y - Configuration.GRID_SIZE,
                            ),
                            (
                                prev_x - Configuration.GRID_SIZE,
                                prev_y + Configuration.GRID_SIZE,
                            ),
                            (
                                prev_x + Configuration.GRID_SIZE,
                                prev_y - Configuration.GRID_SIZE,
                            ),
                            (
                                prev_x + Configuration.GRID_SIZE,
                                prev_y + Configuration.GRID_SIZE,
                            ),
                        ]
                        if Coordinates.in_range_cell((x, y))
                    ]
                    points = np.array([(x, y) for x, y in points])
                    c_hull = ConvexHull(points)

                c_vertices = [
                    (points[vertex, 0], points[vertex, 1]) for vertex in c_hull.vertices
                ]

                if not Polygon(c_vertices).contains(Point(x_cell, y_cell)):
                    x_cell, y_cell = Sampling.sample_closest(
                        (x_cell, y_cell), c_vertices
                    )

                vertex_set = {}
                for x in c_vertices:
                    for y in c_vertices:
                        if x == y:
                            continue
                        vertex_set[(x[0] - y[0], x[1] - y[1])] = 1
                s_points = np.array(list(vertex_set.keys()))

                s_hull = ConvexHull(s_points)

                s_vertices = [
                    (s_points[vertex, 0], s_points[vertex, 1])
                    for vertex in s_hull.vertices
                ]
                p = Polygon(s_vertices)

                t_value = None
                l = 1
                while True:
                    sampled_points = [Sampling.sample_uniformly(p) for _ in range(l)]

                    def get_new_t(points):
                        t_sum = 0
                        for x, y in points:
                            t_sum += x * x + y * y
                        return (t_sum / l) ** (-0.5)

                    new_t = get_new_t(sampled_points)
                    if t_value == None or abs(new_t - t_value) > 1e-3:
                        t_value = new_t
                        l += 1
                    else:
                        break

                normalized_vertices = [
                    (x * t_value, y * t_value) for x, y in s_vertices
                ]

                while True:
                    sampled_point = Sampling.sample_uniformly(
                        Polygon(normalized_vertices)
                    )
                    noise_r = random.gamma(3, epsilon ** (-1))
                    final_x, final_y = (
                        x_cell + sampled_point[0] / t_value * noise_r,
                        y_cell + sampled_point[1] / t_value * noise_r,
                    )
                    if Coordinates.in_range_cell((final_x, final_y)):
                        break
                final_x, final_y = int(final_x), int(final_y)

                # update posterior prob
                posterior = np.zeros((Configuration.GRID_SIZE, Configuration.GRID_SIZE))
                prob_from = np.ones((Configuration.GRID_SIZE, Configuration.GRID_SIZE))
                prob_from *= epsilon**2 / 2 / s_hull.area
                sum_prob = 0
                for x in range(Configuration.GRID_SIZE):
                    for y in range(Configuration.GRID_SIZE):
                        prob_from[x, y] *= math.e ** (
                            -epsilon
                            * t_value
                            * math.sqrt((final_x - x) ** 2 + (final_y - y) ** 2)
                        )
                        sum_prob += prior[x, y] * prob_from[x, y]

                if sum_prob <= 0:
                    posterior[final_x][final_y] = 1
                else:
                    for x in range(Configuration.GRID_SIZE):
                        for y in range(Configuration.GRID_SIZE):
                            posterior[x][y] = prior[x, y] * prob_from[x, y] / sum_prob

                prior = np.zeros((Configuration.GRID_SIZE, Configuration.GRID_SIZE))
                dp_distribution = correlation.get_transition((final_x, final_y))

                for x in range(Configuration.GRID_SIZE):
                    for y in range(Configuration.GRID_SIZE):
                        for (tran_x, tran_y), tran_prob in dp_distribution.items():
                            prior[tran_x, tran_y] += posterior[x, y] * tran_prob

                result.append((final_x, final_y, timestamp))
                prev_x, prev_y = final_x, final_y

            return result

        print("Generating dp copies using pim...")
        out_path = Configuration.DP_DATA_PATH.format(dataset.value, "pim")
        Path(out_path).mkdir(parents=True, exist_ok=True)

        for index in tqdm(range(copies)):
            dp_trajectories = Parallel(n_jobs=16, verbose=1)(
                delayed(apply_pim)(t, epsilon, delta_dp, correlation) for t in data
            )
            with open(
                PurePath(
                    Configuration.DP_DATA_PATH.format(dataset.value, "pim"),
                    "{}_{:.3f}_{}.dat".format(dataset.value, epsilon, index),
                ),
                "w",
            ) as f:
                json.dump(dp_trajectories, f)

        print("Generation OK.")
