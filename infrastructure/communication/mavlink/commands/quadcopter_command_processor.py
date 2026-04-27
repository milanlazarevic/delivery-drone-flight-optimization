from typing import Any, Callable, Dict, Tuple

from domain.interfaces.commands.command_processor import CommandProcessor
from .command_names import CommandNames
from .arm_command import ArmCommand
from .takeoff_command import TakeoffCommand
from .clear_mission_command import ClearMissionCommand
from .upload_mission_command import UploadMissionCommand


class QuadCopterCommandProcessor(CommandProcessor):
    """Processor that manages and executes commands."""

    def __init__(self, connection, message_bus):
        super().__init__()
        self.connection = connection
        self._command_registry.update({
            CommandNames.ARM_UP: lambda args: ArmCommand(self.connection,message_bus, args),
            CommandNames.TAKE_OFF: lambda args: TakeoffCommand(self.connection,message_bus, args),
            CommandNames.MISSION_CLEAR_ALL: lambda args: ClearMissionCommand(self.connection,message_bus, args),
            CommandNames.MISSION_UPLOAD: lambda args: UploadMissionCommand(self.connection, message_bus, args)
        })
