import asyncio
import json
import aioredis
from typing import Callable, Coroutine

class SwarmEventBus:
    """Async Pub/Sub event bus for multi-agent communication."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)
        self.pubsub = self.redis.pubsub()

    async def publish(self, channel: str, event_type: str, payload: dict):
        """Publish a structured event to the swarm."""
        message = {
            "type": event_type,
            "data": payload,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str, callback: Callable[[dict], Coroutine]):
        """Listen for events and trigger agent callbacks."""
        await self.pubsub.subscribe(channel)
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                # Dispatch to agent logic
                asyncio.create_task(callback(data))
