from domain.entities.mission import Mission
from domain.entities.route import Route, Waypoint
from domain.interfaces.path_optimization_strategy import PathOptimizationStrategy
from typing import List
from math import sqrt


class GreedyPathOptimizationStrategy(PathOptimizationStrategy):

    def optimize(self, mission: Mission) -> Route:
        waypoints = mission.get_waypoints()
        # first waypoint is waypoint command and
        # second is takeoff command with same location we always start from there
        optimized = [waypoints[0], waypoints[1]]

        # last waypoint could be RTH command
        if waypoints[-1].lat == 0 and waypoints[-1].lon == 0:
            optimized_waypoints = self._find_greedy(waypoints[0], waypoints[2:-1])
            optimized.extend(optimized_waypoints)
            optimized.append(waypoints[-1])
        else:
            optimized_waypoints = self._find_greedy(waypoints[0], waypoints[2:])
            optimized.extend(optimized_waypoints)

        return Route(optimized)

    def _find_greedy(
        self, start_location: Waypoint, waypoints: List[Waypoint]
    ) -> List[Waypoint]:
        result: List[Waypoint] = []
        curr = (start_location.lat, start_location.lon)
        points_queue = list(waypoints)
        while len(points_queue) > 0:
            nearest_point = None
            nearest_distance = float("inf")
            nearest_idx = -1

            for i, wp in enumerate(points_queue):
                distance = self._calculate_euclidean_distance(
                    curr[0], curr[1], wp.lat, wp.lon
                )
                if distance < nearest_distance:
                    # we got closer point now updating
                    nearest_distance = distance
                    nearest_point = wp
                    nearest_idx = i
            result.append(nearest_point)
            del points_queue[nearest_idx]
            curr = (nearest_point.lat, nearest_point.lon)

        return result

    def _calculate_euclidean_distance(self, x1, y1, x2, y2) -> float:
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
