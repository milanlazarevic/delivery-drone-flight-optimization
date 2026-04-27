from abc import ABC, abstractmethod
from domain.entities.mission import Mission

class PipelineStep(ABC):
    """
    Abstract base class representing a single step in a mission processing pipeline.

    Each pipeline step takes a Mission as input, applies a transformation
    or validation, and returns a (potentially modified) Mission.

    Methods:
        process(mission: Mission) -> Mission:
            Executes the pipeline step on the given mission.
    """
    @abstractmethod
    def process(self, mission: Mission) -> Mission:
        pass