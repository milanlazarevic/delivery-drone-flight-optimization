from domain.interfaces.commands.command import Command, CommandResult, CommandStatus
from pymavlink import mavutil
from typing import Any, Dict, List

#TODO
class UploadMissionCommand(Command):
    ACK_TIMEOUT = 5.0
    ITEM_TIMEOUT = 5.0

    async def _send(self) -> None:
        """Step 1: tell the FC how many items are coming."""
        waypoints: List[Any] = self.args["waypoints"]
        self.connection.mav.mission_count_send(
            self.connection.target_system,
            self.connection.target_component,
            len(waypoints),
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION,
            0  # opaque_id — always 0 for ArduPilot
        )
        print(f"[DEBUG] Sent MISSION_COUNT({len(waypoints)}), waiting to see what FC replies...")

    async def _wait_for_ack(self) -> CommandResult:
        """
        Drive the full upload handshake:
        FC requests each item → we send it → FC sends MISSION_ACK at the end.
        """
        waypoints: List[Any] = self.args["waypoints"]
        expected_seq = 0

        while True:
            # FC will either request the next item or send final MISSION_ACK
            msg = await self._recv_message("MISSION_REQUEST", timeout=self.ITEM_TIMEOUT)

            if msg is None:
                # check if it's actually a MISSION_ACK (final confirmation)
                ack = await self._recv_message("MISSION_ACK", timeout=self.ITEM_TIMEOUT)
                if ack is None:
                    return self._result(
                        False, CommandStatus.TIMEOUT,
                        f"Timeout waiting for MISSION_REQUEST_INT seq={expected_seq}"
                    )
                # got MISSION_ACK without finishing all items — FC rejected mid-upload
                return self._result(
                    False, CommandStatus.FAILED,
                    f"Upload aborted by FC at seq={expected_seq}: MAV_MISSION_RESULT={ack.type}"
                )

            seq = msg.seq

            if seq != expected_seq:
                return self._result(
                    False, CommandStatus.FAILED,
                    f"FC requested seq={seq} but expected seq={expected_seq}"
                )

            if seq >= len(waypoints):
                return self._result(
                    False, CommandStatus.FAILED,
                    f"FC requested seq={seq} but only {len(waypoints)} waypoints available"
                )

            # send the requested item
            wp = waypoints[seq]
            self.connection.mav.mission_item_int_send(
                self.connection.target_system,
                self.connection.target_component,
                seq,
                wp.frame,
                wp.command,
                1 if seq == 0 else 0,   # current
                1,                       # autocontinue
                wp.param1,
                wp.param2,
                wp.param3,
                wp.param4,
                wp.lat,
                wp.lon,
                wp.alt,
                mavutil.mavlink.MAV_MISSION_TYPE_MISSION
            )

            expected_seq += 1

            # all items sent — wait for final MISSION_ACK
            if expected_seq == len(waypoints):
                ack = await self._recv_message("MISSION_ACK", timeout=self.ACK_TIMEOUT)

                if ack is None:
                    return self._result(
                        False, CommandStatus.TIMEOUT,
                        "Timeout waiting for final MISSION_ACK"
                    )

                if ack.type != mavutil.mavlink.MAV_MISSION_ACCEPTED:
                    return self._result(
                        False, CommandStatus.FAILED,
                        f"Mission rejected by FC: MAV_MISSION_RESULT={ack.type}"
                    )

                return self._result(
                    True, CommandStatus.ACKED,
                    f"Mission uploaded successfully ({len(waypoints)} items)"
                )

    async def _validate_state(self) -> CommandResult:
        return self._result(True, CommandStatus.SUCCESS, "Mission upload complete")