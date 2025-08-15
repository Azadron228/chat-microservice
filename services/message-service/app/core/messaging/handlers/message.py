from datetime import datetime
import logging
from app.domain.service import MessageService
from app.domain.repo import MessageRepository
from app.core.casssandra import get_session
from app.core.messaging.factory import broker
logger = logging.getLogger(__name__)


async def handle_new_message(data: dict):
    """Handle incoming messages from NATS."""
    try:
        async with get_session() as session:
            service = MessageService(repo=MessageRepository(session), broker=broker)
            await service.create_message(
                content=data["content"],
                room_id=data["room_id"],
                author_id=data["author_id"],
            )
        logger.info(f"Processed new message from NATS {data}")

    except Exception as e:
        logger.error(f"Error processing new message: {str(e)}")
