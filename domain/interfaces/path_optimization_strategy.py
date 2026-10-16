from abc import ABC, abstractmethod
from domain.entities.mission import Mission
from domain.entities.route import Route


class PathOptimizationStrategy(ABC):
    """
    Abstract base class for path optimization strategies.

    Defines the interface for algorithms that take a mission as input
    and produce an optimized route based on specific optimization criteria
    (e.g. shortest path, minimal energy consumption, obstacle avoidance).

    Methods:
        optimize(mission: Mission) -> Route:
            Computes and returns an optimized route derived from the given mission.
    """

    @abstractmethod
    def optimize(self, mission: Mission) -> Route:
        """
        Optimizes the given mission and returns a corresponding route.

        Args:
            mission (Mission): Mission containing waypoints to be optimized.

        Returns:
            Route: Optimized route generated from the mission.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass
