from domain.interfaces.commands.command import Command, CommandResult, CommandStatus
from pymavlink import mavutil


class ClearMissionCommand(Command):
    ACK_TIMEOUT = 5.0

    async def _send(self) -> None:
        self.connection.mav.mission_clear_all_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )

    def _get_command_id(self) -> int:
        return 1

    async def _validate_state(self) -> CommandResult:
        return self._result(True, CommandStatus.SUCCESS, "Mission cleared")