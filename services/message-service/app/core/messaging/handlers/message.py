from datetime import datetime
import logging
from app.domain.service import MessageService
from app.domain.repo import MessageRepository
from app.core.casssandra import get_session

logger = logging.getLogger(__name__)


async def handle_new_message(data: dict):
    """Handle incoming messages from NATS."""
    try:
        async with get_session() as session:
            service = MessageService(repo=MessageRepository(session))
            await service.create_message(
                content=data["content"],
                room_id=data["room_id"],
                sender_id=data["author_id"],
            )
        logger.info(f"Processed new message from NATS {data}")

    except Exception as e:
        logger.error(f"Error processing new message: {str(e)}")
