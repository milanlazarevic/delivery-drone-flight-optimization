import asyncio
import threading
from infrastructure.communication.mavlink.proxy.mavlink_proxy import MavlinkProxy
from infrastructure.communication.mavlink.proxy.message_bus import MavlinkMessageBus
from application.services.mission_interceptor import MissionInterceptor
from application.services.mission_service import MissionService


mission_interceptor = MissionInterceptor()
message_bus = MavlinkMessageBus()
_loop: asyncio.AbstractEventLoop = None
proxy: MavlinkProxy = None

async def main():
    global _loop, proxy

    _loop = asyncio.get_running_loop()

    # set loop on bus before proxy thread starts publishing
    message_bus.set_loop(_loop)


    proxy = MavlinkProxy(mission_interceptor, message_bus)
    service = MissionService(proxy, message_bus, _loop)
    mission_interceptor.set_callback(service.on_mission_received)

    thread = threading.Thread(target=proxy.initialize_connection, daemon=True)
    thread.start()

    print("Event loop running, waiting for missions...")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())