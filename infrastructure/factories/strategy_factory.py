from infrastructure.algorithms.greedy_strategy import GreedyPathOptimizationStrategy


class StrategyFactory:
    STRATEGY_REGISTRY = {
        "simple": GreedyPathOptimizationStrategy,
    }

    @staticmethod
    def create(strategy_cfg: dict):
        strategy_type = strategy_cfg["type"]
        if strategy_type not in StrategyFactory.STRATEGY_REGISTRY:
            raise ValueError(f"Unknown pipeline step: {strategy_type}")

        return StrategyFactory.STRATEGY_REGISTRY[strategy_type]()
