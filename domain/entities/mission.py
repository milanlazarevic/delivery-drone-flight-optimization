from .waypoint import Waypoint
from typing import List

class Mission:
    """
    Represents a drone mission consisting of an ordered list of waypoints
    and optional metadata.

    Args:
        waypoints (List[Waypoint]): Ordered list of waypoints that define the mission route.
        metadata (dict | None, optional): Additional mission-related data such as
            name, description, or custom parameters. Defaults to None.

    Attributes:
        waypoints (List[Waypoint]): List of mission waypoints.
        metadata (dict): Dictionary containing additional mission data.
    """

    def __init__(self, waypoints: List[Waypoint], metadata: dict | None = None):
        self.waypoints = waypoints
        self.metadata = metadata or {}

    def get_waypoints(self) -> List[Waypoint]:
        """
        Returns the list of waypoints in the mission.

        Returns:
            List[Waypoint]: Ordered list of waypoints.
        """
        return self.waypoints