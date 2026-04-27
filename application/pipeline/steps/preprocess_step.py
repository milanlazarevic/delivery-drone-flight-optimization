from domain.entities.mission import Mission
from ..pipeline import PipelineStep

class PreprocessStep(PipelineStep):
    """Preprocess mission waypoints to specific format Ardupilot expects"""
    def process(self, mission: Mission) -> Mission:
        if mission is None:
            raise ValueError("Mission is None")

        waypoints = mission.get_waypoints()

        if not waypoints:
            raise ValueError("Mission has no waypoints")

        for wp in waypoints:
            wp.lat = int(wp.lat*int(1e7))
            wp.lon = int(wp.lon*int(1e7))

        return mission