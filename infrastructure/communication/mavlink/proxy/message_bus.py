import asyncio
from collections import defaultdict
from typing import Any, Dict, List


class MavlinkMessageBus:
    def __init__(self):
        """
        Message bus used for storing every message from proxy communication.
        Thread safe.

        When MavlinkProxy publishes a message it automatically sends it to this message bus.
        publish method than sends notification for each subscriber that it got new message.

        Subscribers are then used in command pattern to wait for ACK responses later on.

        Reason for this object is that without it proxy will eat each message and in command methods,
        when we have to wait for ACK response we will get TimeLimit exceeded.

        This stores each message so we can access it later and react on it.
        """
        self._queues: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._loop: asyncio.AbstractEventLoop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self, msg_type: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self._queues[msg_type].append(q)
        return q

    def unsubscribe(self, msg_type: str, queue: asyncio.Queue):
        try:
            self._queues[msg_type].remove(queue)
        except ValueError:
            raise ValueError("Queue doesnt exist!")

    def publish(self, msg_type: str, msg: Any):
        """Called from proxy thread — thread-safe."""
        if self._loop is None:
            return
        for q in list(self._queues.get(msg_type, [])):
            self._loop.call_soon_threadsafe(q.put_nowait, msg)
