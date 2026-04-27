from domain.entities.mission import Mission
from domain.entities.route import Route
from application.pipeline.pipeline import Pipeline
from application.services.strategy_selector import StrategySelector

class OptimizeMissionUseCase:
    """
    Use case responsible for optimizing a mission into an execution route.

    Workflow:
    1. Run mission through processing pipeline
    2. Select best optimization strategy based on mission
    3. Apply optimization strategy to produce final route
    """
    def __init__(self, pipeline: Pipeline, strategy_selector: StrategySelector):
        self.pipeline = pipeline
        self.strategy_selector = strategy_selector

    def execute(self, mission: Mission) -> Route:
        strategy = self.strategy_selector.select()

        mission = self.pipeline.run(mission)

        route = strategy.optimize(mission)

        return route
