from domain.interfaces.commands.command_processor import CommandProcessor
from infrastructure.communication.mavlink.commands.command_names import CommandNames
from domain.entities.route import Route
import asyncio


class ExecuteRouteUseCase:
    """
    Use case responsible for sending updated commands to ArduPilot SITL.

    Workflow:
    1. Clear mission that is existing on ArduPilot SITL uploaded from QGC
    2. Upload new optimized mission to ArduPilot SITL
    """

    def __init__(self, command_processor: CommandProcessor):
        self.command_processor = command_processor

    async def execute_route(self, route: Route) -> bool:
        commands = [
            (CommandNames.MISSION_CLEAR_ALL, {}),
            (CommandNames.MISSION_UPLOAD, {"waypoints": route.waypoints}),
        ]

        results = []
        for cmd, args in commands:
            results.append(await self.command_processor.execute_command(cmd, args))

        success = all(r.success for r in results)
        print(results)
        print(
            f"\nMission {'complete' if success else 'aborted'}: "
            f"{sum(r.success for r in results)}/{len(results)} commands succeeded."
        )
        return success

    async def wait_for(self, msg_type, timeout=5):
        start = asyncio.get_event_loop().time()

        while True:
            msg = self.conn.recv_match(type=msg_type, blocking=False)
            if msg:
                return msg

            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError(f"Timeout waiting for {msg_type}")

            await asyncio.sleep(0.01)
