import asyncio
from contextlib import asynccontextmanager
import logging
from app.core.messaging.factory import broker
import app.core.logging
import app.core.messaging.handlers
from app.core.messaging.handlers.message import handle_new_message
from app.core.messaging.factory import broker


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan():
    await broker.connect()
    logger.info("Connected to broker")
    try:
        yield
    finally:
        await broker.close()
        logger.info("Broker connection closed")


async def main():
    async with lifespan():
        try:
            await broker.subscribe("chat.messages.message.to_save",handle_new_message)
            await asyncio.sleep(100)  # Keep the server running indefinitely
        except KeyboardInterrupt:
            await exit()


if __name__ == "__main__":
    asyncio.run(main())