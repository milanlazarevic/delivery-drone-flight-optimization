from domain.interfaces.commands.command import Command, CommandResult, CommandStatus
from typing import Any, Dict, Tuple
from pymavlink import mavutil
import time

class ArmCommand(Command):
    ACK_TIMEOUT   = 5.0
    STATE_TIMEOUT = 10.0

    async def _send(self) -> None:
        self.connection.mav.command_long_send(
            self.connection.target_system, 
            self.connection.target_component, 
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,
            0,0,0,0,0,0
            )

    def _get_command_id(self) -> int:
        return mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM

    async def _validate_state(self) -> CommandResult:
        deadline = time.monotonic() + self.STATE_TIMEOUT

        while time.monotonic() < deadline:
            msg = await self._recv_message("HEARTBEAT")

            if msg is None:
                continue

            is_armed = (
                msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
            )
            if is_armed:
                return self._result(True, CommandStatus.SUCCESS, "Vehicle armed")

        return self._result(False, CommandStatus.TIMEOUT, "Timeout: vehicle never armed")
