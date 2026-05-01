from domain.interfaces.commands.command_processor import CommandProcessor
from .command_names import CommandNames
from .clear_mission_command import ClearMissionCommand
from .upload_mission_command import UploadMissionCommand


class QuadCopterCommandProcessor(CommandProcessor):
    """Processor that manages and executes commands."""

    def __init__(self, connection, message_bus):
        super().__init__()
        self.connection = connection
        self._command_registry.update(
            {
                CommandNames.MISSION_CLEAR_ALL: lambda args: ClearMissionCommand(
                    self.connection, message_bus, args
                ),
                CommandNames.MISSION_UPLOAD: lambda args: UploadMissionCommand(
                    self.connection, message_bus, args
                ),
            }
        )
