from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime
from app.domain.repo import MessageRepository, message_repo_factory
from app.core.messaging.factory import broker

logger = logging.getLogger(__name__)


from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid1

@dataclass
class Message:
    room_id: UUID
    message_id: int
    author_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
    media_ids: List[UUID] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "room_id": str(self.room_id),
            "message_id": self.message_id,
            "author_id": str(self.author_id),
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "media_ids": [str(mid) for mid in self.media_ids],
        }


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

        message_id = await self.repo.save_message(
            room_id=UUID(room_id),
            author_id=UUID(author_id),
            content=content,
            media_ids=media_ids,
        )

        message = Message(
            room_id=room_id,
            message_id=message_id,
            author_id=author_id,
            content=content,
            media_ids=media_ids or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # You may want to serialize before publishing
        await self.broker.publish("chat.messages.to_broadcast", message.to_dict())
        await self.broker.publish("chat.room.update_list", message.to_dict())

        return message.to_dict()
    
    async def list_messages(
        self,
        room_id: UUID,
        before: UUID | None = None,
        after: UUID | None = None,
        limit: int = 10
    ):
        rows = await self.repo.list_messages(room_id,before=before, after=after, limit=limit)

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