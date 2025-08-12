import uuid
import logging
from datetime import datetime
from app.domain.repo import MessageRepository
from app.core.messaging.factory import broker

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo

    async def create_message(self, room_id: str, sender_id: str, content: str) -> dict:
        message_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        message = await self.repo.save_message(
            message_id=message_id,
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            timestamp=timestamp
        )
        
        await broker.publish("message.saved", message)
        logger.info(f"Published new message {message_id} to topic 'message.saved'")
        
        return message
    
    async def get_recent_messages(self, room_id: str, limit: int = 50) -> list:
        """Retrieve recent messages for a room."""
        return await self.repo.get_recent_messages(room_id, limit)