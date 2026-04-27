class Waypoint:
    """
        Initializes a mission waypoint.

        Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        alt (float): Altitude in meters.
        param1 (float): Command-specific parameter (meaning depends on the command).
        param2 (float): Command-specific parameter (meaning depends on the command).
        param3 (float): Command-specific parameter (meaning depends on the command).
        param4 (float): Command-specific parameter (meaning depends on the command).
        frame (int): MAVLink coordinate frame (e.g. MAV_FRAME_GLOBAL_RELATIVE_ALT).
        command (int): MAVLink command ID (e.g. 16 = WAYPOINT, 20 = RETURN_TO_LAUNCH).

        Returns:
        Waypoint: Instance of the Waypoint class.
    """
    def __init__(self,
                lat: float,
                lon: float,
                alt: float,
                param1: float = 0.0,
                param2: float = 0.0,
                param3: float = 0.0,
                param4: float = 0.0,
                frame: int = 0,
                command: int = 0
    ):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4
        self.frame = frame
        self.command = command

    def __str__(self):
        from pymavlink import mavutil
        cmd_name = mavutil.mavlink.enums['MAV_CMD'][self.command].name
        return f"{cmd_name} ({self.lat}, {self.lon}, {self.alt})"
    
    def __repr__(self):
        return self.__str__()