import asyncio
from contextlib import asynccontextmanager
import logging

import grpc
from app.core.messaging.factory import broker
import app.core.logging
import app.core.messaging.handlers
from app.core.messaging.handlers.message import handle_new_message
from app.core.messaging.factory import broker
from app.domain.service import MessageService, get_message_service
from app.core.grpc.message_servicer import MessageServicer
from app.core.grpc.gen.message_pb2_grpc import add_MessageServiceServicer_to_server
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

async def serve_grpc(message_service: MessageService):
    server = grpc.aio.server()
    add_MessageServiceServicer_to_server(
        MessageServicer(message_service), server
    )
    server.add_insecure_port("[::]:50051")
    logger.info("Starting gRPC server on port 50051")
    await server.start()
    await server.wait_for_termination()

async def main():
    # Initialize your MessageService (dependency injection)
    message_service = await get_message_service()
    # Assuming broker is defined (e.g., Redis, RabbitMQ)
    # broker = SomeBroker()  # Initialize your broker here

    async with lifespan(broker):
        try:
            # Start gRPC server and message subscription concurrently
            await asyncio.gather(
                serve_grpc(message_service),
                broker.subscribe("chat.messages.message.to_save", handle_new_message)
            )
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            # Graceful shutdown handled by lifespan context manager

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())