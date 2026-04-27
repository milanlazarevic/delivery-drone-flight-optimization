import asyncio
import threading
from domain.entities.mission import Mission
from application.use_cases.optimize_mission import OptimizeMissionUseCase
from application.services.mission_service import MissionService
from application.services.strategy_selector import StrategySelector
from infrastructure.factories.pipeline_factory import PipelineFactory
from infrastructure.factories.strategy_factory import StrategyFactory
from application.use_cases.execute_mission import ExecuteRouteUseCase
from infrastructure.communication.mavlink.commands.quadcopter_command_processor import QuadCopterCommandProcessor
from infrastructure.communication.mavlink.proxy.mavlink_proxy import MavlinkProxy
from infrastructure.communication.mavlink.proxy.message_bus import MavlinkMessageBus
from application.services.mission_interceptor import MissionInterceptor


mission_interceptor = MissionInterceptor()
message_bus = MavlinkMessageBus()
_loop: asyncio.AbstractEventLoop = None
proxy: MavlinkProxy = None


async def _execute_mission_async(mission: Mission):
    print("Mission arrived in application layer!")
    print(mission.get_waypoints())

    pipeline = PipelineFactory.create([{'type': 'validation'}, {'type': 'preprocessing'}])
    strategy_selector = StrategySelector(strategy=StrategyFactory.create({"type": "simple"}))
    use_case = OptimizeMissionUseCase(pipeline, strategy_selector)
    service = MissionService(use_case)

    route = service.optimize_mission(mission)
    print(route)

    # pass message_bus into command processor so commands read from bus, not recv_match
    command_processor = QuadCopterCommandProcessor(proxy.get_connection(), message_bus)
    route_use_case = ExecuteRouteUseCase(command_processor)

    await route_use_case.execute_route(route)
    print("Route execution complete:", route)


def on_mission_received(mission: Mission):
    print("Mission received, scheduling async execution...")
    future = asyncio.run_coroutine_threadsafe(_execute_mission_async(mission), _loop)

    def _on_done(fut):
        exc = fut.exception()
        if exc:
            print(f"[ERROR] Mission execution failed: {exc}")

    future.add_done_callback(_on_done)


async def main():
    global _loop, proxy

    _loop = asyncio.get_running_loop()

    # set loop on bus before proxy thread starts publishing
    message_bus.set_loop(_loop)

    mission_interceptor.set_callback(on_mission_received)

    # pass message_bus into proxy so it publishes every message
    proxy = MavlinkProxy(mission_interceptor, message_bus)

    thread = threading.Thread(target=proxy.initialize_connection, daemon=True)
    thread.start()

    print("Event loop running, waiting for missions...")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())