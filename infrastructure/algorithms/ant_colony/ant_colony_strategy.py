from domain.entities.mission import Mission
from domain.entities.route import Route, Waypoint
from domain.interfaces.path_optimization_strategy import PathOptimizationStrategy
from typing import List
from math import sqrt
from .constants import *
import numpy as np
import math
from typing import Tuple


class AntColonyPathOptimizationStrategy(PathOptimizationStrategy):

    def __init__(self):
        # for now using default parameters
        self._alpha = ALPHA
        self._beta = BETA
        self._num_ants = NUM_ANTS
        self._evaporation_rate = EVAPORATION_RATE
        self._num_iterations = NUM_OF_ITERATIONS

        self._best_path = None

        self._feromone_matrix = None
        self._visibility_matrix = None
        self._distance_matrix = None

        self._last_run_time = None

    def optimize(self, mission: Mission) -> Route:
        # first waypoint is waypoint command of the starting position (it is fixed) and
        # second is takeoff command with same location we always start from there
        waypoints = mission.get_waypoints()

        start = waypoints[0]
        takeoff = waypoints[1]
        middle = waypoints[2:-1]
        end = waypoints[-1]

        optimized_middle = self._ant_colony_tsp(middle)

        return Route([start, takeoff, *optimized_middle, end])

    def _ant_colony_tsp(self, waypoints: List[Waypoint]) -> List[Waypoint]:
        self.waypoints = waypoints
        self.num_waypoints = len(self.waypoints)
        self._init()

        for _ in range(self._num_iterations):
            all_paths = []
            for _ in range(self._num_ants):
                single_ant_path = self._ant_run()
                all_paths.append(single_ant_path)

            best_iter_path = min(all_paths, key=lambda path: path[1])
            if best_iter_path[1] < self._best_path[1]:
                self._best_path = best_iter_path

            self._update_feromone(all_paths)
            self._update_best_path_feromone()
        return self._remap_indices_to_waypoints(self._best_path)

    def _init(self):
        """
        Initialization before the run of the algorithm.
        Initializes feromone, distance and visibility matrices, as well as best path.
        """
        self._feromone_matrix = np.ones((self.num_waypoints, self.num_waypoints))
        self._fill_distance_matrix()
        self._visibility_matrix = 1 / (self._distance_matrix + 1e-8)
        self._best_path = ([], math.inf)

    def _fill_distance_matrix(self):
        """
        Assignes values to the distance matrix by calculating
        the mutual distance of every two cities.
        """
        self._distance_matrix = np.zeros(
            (self.num_waypoints, self.num_waypoints), dtype=np.float64
        )
        for i, point1 in enumerate(self.waypoints):
            for j, point2 in enumerate(self.waypoints):
                self._distance_matrix[i][j] = self._calculate_euclidean_distance(
                    point1.lat, point1.lon, point2.lat, point2.lon
                )

    def _ant_run(self) -> Tuple[List[int], float]:
        """
        Runs a single iteration trip by one ant.
        Returns a tuple in which the first element is the list of indices of cities in the order of traversal
        and the second element is the total weight of the traversed edges.
        """
        # choose starting waypoint
        start = np.random.randint(0, self.num_waypoints)

        tour = []
        visited = set()
        total_dist = 0

        curr_wp = start
        visited.add(curr_wp)
        tour.append(curr_wp)
        for _ in range(self.num_waypoints - 1):
            probability = (self._feromone_matrix[curr_wp] ** self._alpha) * (
                self._visibility_matrix[curr_wp] ** self._beta
            )
            for i in range(self.num_waypoints):
                if i in visited:
                    probability[i] = 0
            # probability for each city to visit: [0.2, 0.3, 0.5]
            probability /= np.sum(probability)

            next_wp = np.random.choice(np.arange(self.num_waypoints), p=probability)
            total_dist += self._distance_matrix[curr_wp][next_wp]

            curr_wp = next_wp
            visited.add(curr_wp)
            tour.append(curr_wp)

        return tour, total_dist

    def _update_feromone(self, all_paths: List[Tuple[List[int], float]]) -> None:
        """
        Updates feromone levels for next iteration by its evaporation rate and adding feromone on ants paths.
        """
        self._feromone_matrix = self._feromone_matrix * (1 - self._evaporation_rate)

        for tour, distance in all_paths:
            for i in range(len(tour) - 1):
                start_wp, end_wp = tour[i], tour[i + 1]
                self._feromone_matrix[start_wp][end_wp] += 1 / distance

    def _update_best_path_feromone(self):
        """
        Adds feromone on the global best path.
        Use this at the end of each iteration to implement elitist ant system version of the algorithm.
        """
        tour, distance = self._best_path
        for i in range(len(tour) - 1):
            start_wp, end_wp = tour[i], tour[i + 1]
            self._feromone_matrix[start_wp][end_wp] += 1 / distance

    def _remap_indices_to_waypoints(
        self, ant_path: Tuple[List[int], float]
    ) -> List[Waypoint]:
        path, score = ant_path
        print(f"Best score TSP could get: {score}")

        result = []

        for i in path:
            result.append(self.waypoints[i])

        return result

    def _calculate_euclidean_distance(self, x1, y1, x2, y2) -> float:
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
