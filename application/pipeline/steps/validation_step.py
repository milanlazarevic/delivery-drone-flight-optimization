from domain.entities.mission import Mission
from ..pipeline import PipelineStep


class ValidationStep(PipelineStep):
    """Validates each mission waypoint."""

    def process(self, mission: Mission) -> Mission:
        if mission is None:
            raise ValueError("Mission is None")

        waypoints = mission.get_waypoints()

        if not waypoints:
            raise ValueError("Mission has no waypoints")

        for wp in waypoints:
            if not (-90 <= wp.lat <= 90):
                raise ValueError("Invalid latitude")

            if not (-180 <= wp.lon <= 180):
                raise ValueError("Invalid longitude")

            if wp.alt < 0:
                raise ValueError("Invalid altitude")

        return mission
