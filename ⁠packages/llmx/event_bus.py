import asyncio
import json
import logging
from typing import Callable, Coroutine, Any, Dict
import redis.asyncio as aioredis

logger = logging.getLogger("LLMX.EventBus")
logging.basicConfig(level=logging.INFO)

class SwarmEventBus:
    """Async Pub/Sub event bus for multi-agent coordination using Redis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: aioredis.Redis | None = None
        self.pubsub: aioredis.client.PubSub | None = None

    async def connect(self):
        """Establishes connection to the Redis event broker."""
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        logger.info(f"Connected to Redis event bus at {self.redis_url}")

    async def publish(self, channel: str, event_type: str, payload: Dict[str, Any]):
        """Publish a structured JSON event to a specific swarm channel."""
        if not self.redis:
            await self.connect()

        message = {
            "type": event_type,
            "data": payload,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.redis.publish(channel, json.dumps(message))
        logger.debug(f"Published event [{event_type}] to channel [{channel}]")

    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Coroutine]):
        """Subscribe to a channel and dispatch incoming messages to an async callback."""
        if not self.pubsub:
            if not self.redis:
                await self.connect()
            self.pubsub = self.redis.pubsub()

        await self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to swarm channel: {channel}")

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        asyncio.create_task(callback(data))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message on {channel}: {e}")
        except Exception as e:
            logger.error(f"Subscription stream interrupted on {channel}: {e}")
        finally:
            await self.pubsub.unsubscribe(channel)
