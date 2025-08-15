import json
from typing import List, Optional
from uuid import UUID
import uuid
import logging
from datetime import datetime
from app.domain.repo import MessageRepository, message_repo_factory
from app.core.messaging.factory import broker
from app.core.casssandra import get_session
logger = logging.getLogger(__name__)
class MessageService:
    def __init__(self, repo: MessageRepository, broker):
        self.repo = repo
        self.broker = broker

    async def create_message(
        self,
        room_id: UUID,
        author_id: UUID,
        content: str,
        media_ids: Optional[List[UUID]] = None
    ) -> dict:
        message_id = uuid.uuid1()  # UUID1 for chronological order
        timestamp = datetime.now()
        room_id = UUID(room_id)
        author_id = UUID(author_id)

        message = {
            "message_id": str(message_id),
            "room_id": str(room_id),
            "author_id": str(author_id),
            "content": content,
            "media_ids": [str(mid) for mid in (media_ids or [])],
            "created_at": timestamp.isoformat()
        }
        logger.info(f"Type of room_id: {type(room_id)}")

        await self.repo.save_message(
            room_id=room_id,
            message_id=message_id,
            author_id=author_id,
            content=content,
            media_ids=media_ids,
            timestamp=timestamp
        )

        # Publish event for broadcasting
        await self.broker.publish("chat.messages.to_broadcast", message)

        return message
    
    async def list_messages(
        self,
        room_id: UUID,
        limit: int = 50
    ):
        rows = await self.repo.list_messages(room_id, limit)

        # Convert rows to JSON-serializable dicts
        messages = []
        for row in rows:
            messages.append({
                "room_id": str(row.room_id),
                "message_id": str(row.message_id),
                "author_id": str(row.author_id),
                "content": row.content,
                "media_ids": [str(mid) for mid in (row.media_ids or [])],
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })

        return messages


    async def update_message(
        self,
        room_id: UUID,
        message_id: UUID,
        content: str
    ):
        updated_at = datetime.utcnow()
        await self.repo.update_message(
            room_id=room_id,
            message_id=message_id,
            content=content,
            updated_at=updated_at
        )
        return {"status": "updated", "updated_at": updated_at.isoformat()}

    async def update_status(
        self,
        message_id: UUID,
        user_id: UUID,
        status: int
    ):
        now = datetime.now()
        delivered_at = now if status == 0 else None
        seen_at = now if status == 1 else None

        await self.repo.update_status(
            message_id=message_id,
            user_id=user_id,
            status=status,
            delivered_at=delivered_at,
            seen_at=seen_at
        )

        return {"status": "status updated", "status_code": status}


async def message_service_factory() -> MessageService:
    repo = await message_repo_factory()
    return MessageService(repo=repo, broker=broker)