import asyncio
from contextlib import asynccontextmanager
import logging

import grpc
from app.core.messaging.factory import broker
import app.core.logging
import app.core.messaging.handlers
from app.core.messaging.handlers.message import handle_new_message
from app.core.messaging.factory import broker
from protos.message_pb2_grpc import add_MessageServiceServicer_to_server
from app.grpc.message_servicer import MessageServicer

logger = logging.getLogger(__name__)


async def serve_grpc():
    server = grpc.aio.server()

    add_MessageServiceServicer_to_server(MessageServicer(), server)

    server.add_insecure_port("[::]:50051")
    logger.info("Starting gRPC server on port 50051")
    await server.start()
    await server.wait_for_termination()
