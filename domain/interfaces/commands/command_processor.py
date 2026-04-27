from typing import Any, Callable, Dict, Tuple

from .command import Command


class CommandProcessor:
    """Processor that manages and executes commands."""

    def __init__(self):
        self._command_registry:Dict[str,Callable[[Dict[str, Any]], Command]] = {}

    def register_command(self, command_name: str, factory: Callable[..., Command]) -> None:
        """
        Register a new command.

        :param command_name: The name of the command to register
        :type command_name: str
        :param command: The command instance to register
        :type command: Command

        :return: None
        :rtype: None
        """
        self._command_registry[command_name] = factory

    async def execute_command(self, command_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute a command by name.

        :param command_name: The name of the command to execute
        :type command_name: str
        :param args: Dictionary of command arguments
        :type args: Dict[str, Any]

        :return: Tuple of success and message
        :rtype: Tuple[bool, str]
        """
        if command_name not in self._command_registry:
            return False, f'Unknown command: {command_name}'

        command = self._command_registry[command_name](args)
        return await command.execute()