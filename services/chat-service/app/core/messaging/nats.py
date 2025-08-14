import json
import logging
from nats.aio.client import Client as NATS
from .base import MessageBroker

logger = logging.getLogger(__name__)


class NATSBroker(MessageBroker):
    def __init__(self, url: str):
        self.url = url
        self.client = NATS()

    async def connect(self):
        try:
            await self.client.connect(servers=[self.url])
        except Exception as e:
            logger.exception("Failed to connect to NATS broker")
            raise

    async def publish(self, topic: str, message: dict):
        try:
            await self.client.publish(topic, json.dumps(message).encode())
        except Exception as e:
            logger.exception(f"Failed to publish to {topic}")
            raise

    async def subscribe(self, topic: str, handler):
        async def wrapper(msg):
            data = json.loads(msg.data.decode())
            try:
                await handler(data)
            except Exception as e:
                logger.exception(f"Error handling message from {topic}")

        await self.client.subscribe(topic, cb=wrapper)
        logger.info(f"Subscribed to topic: {topic}")

    async def close(self):
        await self.client.close()
