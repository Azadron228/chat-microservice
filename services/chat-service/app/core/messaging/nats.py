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
        await self.client.connect(servers=[self.url])

    async def publish(self, topic: str, message: dict):
        await self.client.publish(topic, json.dumps(message).encode())

    async def subscribe(self, topic: str, handler):
        logger.info(f"Subscribed to topic: {topic}")
        async def wrapper(msg):
            data = json.loads(msg.data.decode())
            await handler(data)
        await self.client.subscribe(topic, cb=wrapper)

    async def close(self):
        await self.client.close()
