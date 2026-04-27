import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .command_result import CommandResult, CommandStatus
from pymavlink import mavutil


class Command(ABC):
    """Abstract base class for mission commands sent to Ardupilot SITL"""
    def __init__(self, connection: mavutil.mavfile, message_bus, args: Dict[str, Any]) -> None:
        self.connection = connection
        self.args = args
        self.status = CommandStatus.PENDING
        self._start_time: float = 0.0
        self.message_bus = message_bus

    async def execute(self) -> CommandResult:
        """
        Execute the command.
        """
        self._start_time = time.monotonic()

        try:
            # send command
            self.status = CommandStatus.SENT
            await self._send()

            # get acknowledge
            cmd_ack = await self._wait_for_ack()
            if not cmd_ack.success:
                return cmd_ack
            
            self.status = CommandStatus.ACKED

            self.status = CommandStatus.VALIDATING
            return await self._validate_state()


        except asyncio.CancelledError:
            return self._result(False, CommandStatus.FAILED, "Command cancelled")
        except Exception as e:
            return self._result(False, CommandStatus.FAILED, f"Unexpected error: {e}")
        
    @abstractmethod
    async def _send(self) -> None:
        """Fire the MAVLink message. Do not wait for response here."""
        pass

    @abstractmethod
    def _get_command_id(self) -> int:
        """Return the MAV_CMD_* integer this command sends."""
        pass

    @abstractmethod
    async def _validate_state(self) -> CommandResult:
        """
        Override this in commands that must confirm a vehicle state change
        (e.g. TakeOff must confirm altitude reached, not just ACK).
        Default: ACK alone is sufficient.
        """
        return self._result(True, CommandStatus.SUCCESS, "ACK accepted")

    async def _recv_message(self, msg_type: str, timeout: float = 5.0) -> Any:
        queue = self.message_bus.subscribe(msg_type)
        try:
            return await asyncio.wait_for(queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self.message_bus.unsubscribe(msg_type, queue)

    async def _wait_for_ack(self) -> CommandResult:
        deadline = time.monotonic() + self.ACK_TIMEOUT

        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            msg = await self._recv_message("MISSION_ACK", timeout=remaining)
            if msg is None:
                break  # timeout expired inside _recv_message


            if msg.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                return self._result(True, CommandStatus.ACKED, "ACK accepted")

            reason = self._mav_result_to_str(msg.type)
            return self._result(False, CommandStatus.FAILED, f"ACK rejected: {reason}")

        return self._result(False, CommandStatus.TIMEOUT, "Timeout: no COMMAND_ACK received")

    def _result(
        self,
        success: bool,
        status: CommandStatus,
        message: str,
        extra: Optional[Dict] = None,
    ) -> CommandResult:
        self.status = status
        return CommandResult(
            success=success,
            status=status,
            message=message,
            duration_ms=(time.monotonic() - self._start_time) * 1000,
            extra=extra or {},
        )

    @staticmethod
    def _mav_result_to_str(result: int) -> str:
        return {
            mavutil.mavlink.MAV_MISSION_ERROR: "Generic error / not accepting mission commands at all right now.",
            mavutil.mavlink.MAV_MISSION_UNSUPPORTED_FRAME: "Coordinate frame is not supported.",
            mavutil.mavlink.MAV_MISSION_UNSUPPORTED:          "Command is not supported.",
        }.get(result, f"unknown({result})")
        