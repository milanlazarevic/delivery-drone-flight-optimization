from domain.interfaces.path_optimization_strategy import PathOptimizationStrategy

class StrategySelector:
    """
    Provides access to a selected path optimization strategy.

    This class currently acts as a simple wrapper around a single
    PathOptimizationStrategy instance. It can later be extended to
    support dynamic strategy selection based on mission properties.

    Args:
        strategy (PathOptimizationStrategy): The strategy instance to be used.

    Attributes:
        strategy (PathOptimizationStrategy): Stored optimization strategy.
    """
    def __init__(self, strategy: PathOptimizationStrategy):
        self.strategy = strategy

    def select(self) -> PathOptimizationStrategy:
        return self.strategy