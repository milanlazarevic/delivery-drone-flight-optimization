from typing import List
from domain.entities.mission import Mission
from .pipeline_step import PipelineStep


class Pipeline:
    """
    Represents a sequence of processing steps applied to a mission.

    The pipeline executes each step in order, passing the result of the
    previous step as input to the next one.

    Args:
        steps (List[PipelineStep]): Ordered list of pipeline steps to execute.

    Attributes:
        steps (List[PipelineStep]): List of processing steps.
    """

    def __init__(self, steps: List[PipelineStep]):
        self.steps = steps

    def run(self, mission: Mission) -> Mission:
        current = mission
        for step in self.steps:
            current = step.process(mission)
        return current
