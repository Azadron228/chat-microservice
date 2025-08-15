import asyncio
from contextlib import asynccontextmanager
import logging

import grpc
from app.core.messaging.factory import broker
import app.core.logging
import app.core.messaging.handlers
from app.core.messaging.handlers.message import handle_new_message
from app.core.messaging.factory import broker
from app.grpc.server import serve_grpc

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(broker):
    await broker.connect()
    logger.info("Connected to broker")
    try:
        yield
    finally:
        await broker.close()
        logger.info("Broker connection closed")


async def main():
    async with lifespan(broker):
        try:
            await asyncio.gather(
                serve_grpc(),
                broker.subscribe("chat.messages.message.to_save", handle_new_message),
            )
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
