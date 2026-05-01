from domain.entities.mission import Mission
from domain.entities.route import Route
from application.use_cases.optimize_mission import OptimizeMissionUseCase
import asyncio
from domain.entities.mission import Mission
from application.use_cases.optimize_mission import OptimizeMissionUseCase
from application.services.strategy_selector import StrategySelector
from infrastructure.factories.pipeline_factory import PipelineFactory
from infrastructure.factories.strategy_factory import StrategyFactory
from application.use_cases.execute_mission import ExecuteRouteUseCase
from infrastructure.communication.mavlink.commands.quadcopter_command_processor import QuadCopterCommandProcessor
from infrastructure.communication.mavlink.proxy.mavlink_proxy import MavlinkProxy
from infrastructure.communication.mavlink.proxy.message_bus import MavlinkMessageBus

class MissionService:
    """
    Application service responsible for handling mission-related operations.

    This service acts as a facade over use cases, delegating business logic
    execution while providing a simple interface to higher layers (e.g. API).

    Args:
        optimize_use_case (OptimizeMissionUseCase): Use case responsible for
            optimizing a mission.

    Attributes:
        optimize_use_case (OptimizeMissionUseCase): Mission optimization use case.
    """
    def __init__(self, proxy: MavlinkProxy, message_bus: MavlinkMessageBus, loop: asyncio.AbstractEventLoop):
        self._proxy = proxy
        self._message_bus = message_bus
        self._loop = loop
        self.optimize_use_case = None

    def optimize_mission(self, mission: Mission) -> Route:
        return self.optimize_use_case.execute(mission)
    
    def on_mission_received(self, mission: Mission):
        print("Mission received, scheduling async execution...")
        future = asyncio.run_coroutine_threadsafe(self._execute_mission_async(mission), self._loop)


        future.add_done_callback(self._on_done)
    
    def _create_pipeline(self):
        pipeline = PipelineFactory.create([{'type': 'validation'}, {'type': 'preprocessing'}])
        strategy_selector = StrategySelector(strategy=StrategyFactory.create({"type": "simple"}))
        self.optimize_use_case = OptimizeMissionUseCase(pipeline, strategy_selector)


    async def _execute_mission_async(self, mission: Mission):
        print("Mission arrived in application layer!")
        print(mission.get_waypoints())
        self._create_pipeline()

        route = self.optimize_mission(mission)
        print(route)

        # pass message_bus into command processor so commands read from bus, not recv_match
        command_processor = QuadCopterCommandProcessor(self._proxy.get_connection(), self._message_bus)
        route_use_case = ExecuteRouteUseCase(command_processor)

        await route_use_case.execute_route(route)
        print("Route execution complete:", route)

    
    def _on_done(self, fut):
        exc = fut.exception()
        if exc:
            print(f"[ERROR] Mission execution failed: {exc}")