from domain.interfaces.commands.command import Command, CommandResult, CommandStatus
from pymavlink import mavutil
from typing import List
from domain.entities.waypoint import Waypoint


class UploadMissionCommand(Command):
    """
    1. Send command for uploading mission of n points
    2. Waits for MISSION_REQUEST from ArduPilot - message that says get me the ith waypoint
    3. We then sends the ith endpoint after validation
    4. Wait for the ArduPilot's MISSION_ACK after all items have been sent.
    5. If ack is success mission is uploaded.
    """

    ACK_TIMEOUT = 5.0
    ITEM_TIMEOUT = 5.0

    async def _send(self) -> None:
        """Step 1: tell the FC how many items are coming."""
        self._waypoints: List[Waypoint] = self.args["waypoints"]
        self.connection.mav.mission_count_send(
            self.connection.target_system,
            self.connection.target_component,
            len(self._waypoints),
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
            0,  # opaque_id — always 0 for ArduPilot
        )
        print(
            f"[DEBUG] Sent MISSION_COUNT({len(self._waypoints)}), waiting to see what FC replies..."
        )

    async def _wait_for_ack(self) -> CommandResult:
        """
        Drive the full upload handshake:
        FC requests each item → we send it → FC sends MISSION_ACK at the end.
        """
        items_sent = 0
        while items_sent < len(self._waypoints):
            result = await self._handle_mission_item(items_sent)
            if not result.success:
                return result
            items_sent += 1
        return await self._wait_for_final_ack()

    async def _validate_state(self) -> CommandResult:
        return self._result(True, CommandStatus.SUCCESS, "Mission upload complete")

    async def _handle_mission_item(self, items_sent: int):
        """Wait for the FC to request a specific sequence number, then send it."""

        msg = await self._recv_message("MISSION_REQUEST", timeout=self.ITEM_TIMEOUT)
        if msg is None:
            return self._result(
                False,
                CommandStatus.TIMEOUT,
                f"Timeout waiting for MISSION_REQUEST seq={items_sent}",
            )
        actual_seq = msg.seq
        result = await self._validate_mission_item(actual_seq)
        if not result.success:
            return result
        self._send_waypoint(actual_seq)
        return self._result(True, CommandStatus.SUCCESS, "Item sent")

    async def _validate_mission_item(self, actual_seq: int) -> CommandResult:
        if actual_seq >= len(self._waypoints):
            return self._result(
                False,
                CommandStatus.FAILED,
                f"FC requested seq={actual_seq} but only {len(self._waypoints)} waypoints available",
            )
        return self._result(True, CommandStatus.SUCCESS, "Sequence valid")

    def _send_waypoint(self, seq: int):
        wp = self._waypoints[seq]
        self.connection.mav.mission_item_int_send(
            self.connection.target_system,
            self.connection.target_component,
            seq,
            wp.frame,
            wp.command,
            self._current_flag(seq),  # current
            1,  # autocontinue
            wp.param1,
            wp.param2,
            wp.param3,
            wp.param4,
            wp.lat,
            wp.lon,
            wp.alt,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
        )

    async def _wait_for_final_ack(self):
        """Wait for the FC's MISSION_ACK after all items have been sent."""
        ack = await self._recv_message("MISSION_ACK", timeout=self.ACK_TIMEOUT)

        if ack is None:
            return self._result(
                False, CommandStatus.TIMEOUT, "Timeout waiting for final MISSION_ACK"
            )

        if ack.type != mavutil.mavlink.MAV_MISSION_ACCEPTED:
            return self._result(
                False,
                CommandStatus.FAILED,
                f"Mission rejected by FC: MAV_MISSION_RESULT={ack.type}",
            )

        return self._result(
            True,
            CommandStatus.ACKED,
            f"Mission uploaded successfully ({len(self._waypoints)} items)",
        )

    @staticmethod
    def _current_flag(seq: int) -> int:
        """MAVLink 'current' flag: 1 only for the first item (home position)."""
        return 1 if seq == 0 else 0
