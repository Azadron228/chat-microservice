import asyncio
from contextlib import asynccontextmanager
import logging
from app.core.messaging.factory import broker
import app.core.logging
import app.core.messaging.handlers

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
            # gRPC server should block here
            ...
        except KeyboardInterrupt:
            await exit()


if __name__ == "__main__":
    asyncio.run(main())