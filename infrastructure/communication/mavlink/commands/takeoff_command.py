from domain.interfaces.commands.command import Command, CommandResult, CommandStatus
from typing import Any, Dict, Tuple
from pymavlink import mavutil
import time

class TakeoffCommand(Command):
    ACK_TIMEOUT   = 5.0
    STATE_TIMEOUT    = 30.0
    ALTITUDE_TOLERANCE = 0.95

    async def _send(self) -> None:
        target_alt = self.args.get("altitude", 10.0)
        self.connection.mav.command_long_send(
            self.connection.target_system, 
            self.connection.target_component, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,0,0,0,
            0,0,
            float(target_alt)
            )

    def _get_command_id(self) -> int:
        return mavutil.mavlink.MAV_CMD_NAV_TAKEOFF

    async def _validate_state(self) -> CommandResult:
        deadline = time.monotonic() + self.STATE_TIMEOUT
        target_alt = self.args.get("altitude", 10.0)
        threshold_alt = target_alt * self.ALTITUDE_TOLERANCE

        while time.monotonic() < deadline:
            msg = await self._recv_message("GLOBAL_POSITION_INT")

            if msg is None:
                continue

            current_alt = msg.relative_alt / 1000
            if current_alt >= threshold_alt:
                return self._result(
                    True, 
                    CommandStatus.SUCCESS, 
                    f"Reached {current_alt:.1f}m (target: {target_alt}m)",
                    extra={"final_altitude_m": current_alt}
                    )

        return self._result(
            False,
            CommandStatus.TIMEOUT,
            f"Timeout: only reached {current_alt:.1f}m of {target_alt}m target",
            extra={"final_altitude_m": current_alt},
        )
