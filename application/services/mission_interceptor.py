from domain.entities.waypoint import Waypoint
from domain.entities.mission import Mission


class MissionInterceptor:
    """Intercepts messages from QGC -> ArduPilot SITL that contains MISSION prefix. Specific
    messages are of interest for us to intercept for later path optimization.

    Mavlink protocol goes like this:
    1. MISSION_COUNT is the first message that sends to us "count"
      saying how much MISSION_ITEMS we have in mission

    2. MISSION_ITEM messages are sent after that. There will be
      "count" number of this messages. And when we get to last MISSION_ITEM message
      then we call call_back method => _on_mission_received
    """

    def __init__(self):
        self.waypoints: list[Waypoint] = []
        self.expected_count = None
        self._on_mission_received = None

    def set_callback(self, callback):
        self._on_mission_received = callback

    def set_mission_count(self, count: int):
        self.expected_count = count

    def handle_message(self, msg):
        msg_type = msg.get_type()

        if msg_type == "MISSION_COUNT":
            self._handle_mission_count(msg)

        elif msg_type == "MISSION_ITEM_INT":
            self._handle_mission_item(msg)

    def _handle_mission_count(self, msg):
        self.expected_count = msg.count
        self.waypoints = []

    def _handle_mission_item(self, msg):
        if self.expected_count is None:
            return
        print(msg)

        wp = Waypoint(
            lat=msg.x / 1e7,
            lon=msg.y / 1e7,
            alt=msg.z,
            param1=msg.param1,
            param2=msg.param2,
            param3=msg.param3,
            param4=msg.param4,
            frame=msg.frame,
            command=msg.command,
        )

        self.waypoints.append(wp)

        if self._is_mission_complete():
            self._emit_mission()

    def _is_mission_complete(self):
        return (
            self.expected_count is not None
            and len(self.waypoints) == self.expected_count
        )

    def _emit_mission(self):
        mission = Mission(waypoints=self.waypoints.copy())

        self._expected_count = None
        self._waypoints = []

        if self._on_mission_received:
            self._on_mission_received(mission)
