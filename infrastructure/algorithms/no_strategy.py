from domain.entities.mission import Mission
from domain.entities.route import Route, Waypoint
from domain.interfaces.path_optimization_strategy import PathOptimizationStrategy


class NoOptimizationStrategy(PathOptimizationStrategy):
    # return the mission as is for demonstration purpuses
    def optimize(self, mission: Mission) -> Route:
        waypoints = mission.get_waypoints()

        return Route(waypoints)
