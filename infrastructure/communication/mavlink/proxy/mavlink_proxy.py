from pymavlink import mavutil
import threading
import time
from application.services.mission_interceptor import MissionInterceptor
from domain.entities.waypoint import Waypoint
from .message_bus import MavlinkMessageBus

class MavlinkProxy:
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
        # thread = threading.Thread(target=self._run_connection_loop, daemon=True)
        # thread.start()

        self._run_connection_loop()

        # print("Proxy started in background thread")

    def _run_connection_loop(self):
        while True:
            # SITL -> QGC
            msg = self.sitl.recv_match(blocking=False)
            if msg:
                # if "MISSION" in msg.get_type():
                    # print(f"[DEBUG BUS] {msg.get_type()}")
                buf = msg.get_msgbuf()
                if buf:
                    self.qgc.write(buf)
                self.message_bus.publish(msg.get_type(), msg)

            # QGC -> SITL (commands from QGC)
            msg = self.qgc.recv_match(blocking=False)
            if msg:
                self.mission_interceptor.handle_message(msg)
                # print(msg.get_srcSystem())
                buf = msg.get_msgbuf()
                if buf:
                    self.sitl.write(buf)
                # self.message_bus.publish(msg.get_type(), msg)
            # time.sleep(0.001)

    def get_mission(self):
        return 0
    
    def get_connection(self) -> mavutil.mavfile:
        return self.sitl