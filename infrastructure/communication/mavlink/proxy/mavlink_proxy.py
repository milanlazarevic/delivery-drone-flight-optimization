from pymavlink import mavutil
from application.services.mission_interceptor import MissionInterceptor
from domain.entities.waypoint import Waypoint
from .message_bus import MavlinkMessageBus

class MavlinkProxy:
    """
    Proxy for mavlink communication between QGC and Ardupilot SITL.
    Intended to be used in the separate thread as it is a blocking operation.

    Mission interceptor is used to wait for specific messages and it should call
    a callback.
    """
    def __init__(self, mission_interceptor: MissionInterceptor, message_bus: MavlinkMessageBus):
        self.sitl = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
        self.qgc  = mavutil.mavlink_connection('udpout:127.0.0.1:14560')
        self._running = False
        self.mission_interceptor = mission_interceptor
        self.message_bus = message_bus

    def initialize_connection(self):
        self._running = True

        print("Waiting for SITL heartbeat...")
        self.sitl.wait_heartbeat()
        print(f"SITL connected (system={self.sitl.target_system}, \
               component={self.sitl.target_component})")
        self._run_connection_loop()


    def _run_connection_loop(self):
        while True:
            # SITL -> QGC
            msg = self.sitl.recv_match(blocking=False)
            if msg:
                buf = msg.get_msgbuf()
                if buf:
                    self.qgc.write(buf)
                self.message_bus.publish(msg.get_type(), msg)

            # QGC -> SITL (commands from QGC)
            msg = self.qgc.recv_match(blocking=False)
            if msg:
                self.mission_interceptor.handle_message(msg)
                buf = msg.get_msgbuf()
                if buf:
                    self.sitl.write(buf)

    def get_mission(self):
        return 0
    
    def get_connection(self) -> mavutil.mavfile:
        return self.sitl