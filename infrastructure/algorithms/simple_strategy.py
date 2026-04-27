from domain.entities.mission import Mission
from domain.entities.route import Route
from domain.interfaces.path_optimization_strategy import PathOptimizationStrategy

class SimplePathOptimizationStrategy(PathOptimizationStrategy):

    def optimize(self, mission: Mission) -> Route:
        waypoints = mission.get_waypoints()

        optimized = waypoints[:2] + [waypoints[3], waypoints[2], waypoints[-1]]

        return Route(optimized)