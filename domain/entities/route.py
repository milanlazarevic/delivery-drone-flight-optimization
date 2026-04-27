from typing import List
from .waypoint import Waypoint

class Route:
    """
    Represents a route composed of an ordered sequence of waypoints. It is
    used as return value for optimized mission.

    Args:
        waypoints (List[Waypoint]): List of waypoints defining the route.

    Attributes:
        waypoints (List[Waypoint]): Ordered list of route waypoints.
    """
    def __init__(self, waypoints: List[Waypoint]):
        self.waypoints = waypoints

    def __str__(self):
        result = [f"{i+1}. {point}" for i, point in enumerate(self.waypoints)]
        return "Route:\n" + "\n".join(result)
    
 