from datetime import datetime
import logging
from app.domain.service import MessageService
from app.domain.repo import MessageRepository


logger = logging.getLogger(__name__)


async def handle_new_message(self, data: dict):
    """Handle incoming messages from NATS."""
    try:
        service = MessageService(repo=MessageRepository())
        service.create_message(data)
        logger.info(f"Processed new message {data['message_id']} from NATS")

    except Exception as e:
        logger.error(f"Error processing new message: {str(e)}")
