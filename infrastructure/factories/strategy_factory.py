from infrastructure.algorithms.greedy_strategy import GreedyPathOptimizationStrategy
from infrastructure.algorithms.ant_colony.ant_colony_strategy import (
    AntColonyPathOptimizationStrategy,
)
from infrastructure.algorithms.no_strategy import NoOptimizationStrategy


class StrategyFactory:
    STRATEGY_REGISTRY = {
        "simple": GreedyPathOptimizationStrategy,
        "ant-colony": AntColonyPathOptimizationStrategy,
        "no-strategy": NoOptimizationStrategy,
    }

    @staticmethod
    def create(strategy_cfg: dict):
        strategy_type = strategy_cfg["type"]
        if strategy_type not in StrategyFactory.STRATEGY_REGISTRY:
            raise ValueError(f"Unknown pipeline step: {strategy_type}")

        return StrategyFactory.STRATEGY_REGISTRY[strategy_type]()
