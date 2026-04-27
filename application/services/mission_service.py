from domain.entities.mission import Mission
from domain.entities.route import Route
from application.use_cases.optimize_mission import OptimizeMissionUseCase


class MissionService:
    """
    Application service responsible for handling mission-related operations.

    This service acts as a facade over use cases, delegating business logic
    execution while providing a simple interface to higher layers (e.g. API).

    Args:
        optimize_use_case (OptimizeMissionUseCase): Use case responsible for
            optimizing a mission.

    Attributes:
        optimize_use_case (OptimizeMissionUseCase): Mission optimization use case.
    """
    def __init__(self, optimize_use_case: OptimizeMissionUseCase):
        self.optimize_use_case = optimize_use_case

    def optimize_mission(self, mission: Mission) -> Route:
        return self.optimize_use_case.execute(mission)