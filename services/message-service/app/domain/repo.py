import logging
from cassandra.query import PreparedStatement
from uuid import UUID
from datetime import datetime


import uuid
from datetime import datetime
from cassandra.cluster import Session, PreparedStatement
from typing import List, Optional
from uuid import UUID
from app.domain.schemas import MessageCreate, MessageOut

logger = logging.getLogger(__name__)


class MessageRepository:
    def __init__(self, session: Session):
        self.session = session
        self._prepare_statements()

    def _prepare_statements(self) -> None:
        """Prepare all Cassandra prepared statements for the repository."""
        # Insert message into chat.messages
        self.insert_message_ps: PreparedStatement = self.session.prepare("""
            INSERT INTO chat.messages (
                room_id, bucket, message_id, author_id,
                content, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)

        # Select messages by room_id and bucket
        self.select_messages_by_room_ps: PreparedStatement = self.session.prepare("""
            SELECT room_id, bucket, message_id, author_id, content, status, created_at, updated_at
            FROM chat.messages
            WHERE room_id = ? AND bucket = ?
            ORDER BY message_id DESC
        """)

        # Select messages before a specific message
        self.select_messages_before_ps: PreparedStatement = self.session.prepare("""
            SELECT room_id, bucket, message_id, author_id, content, status, created_at, updated_at
            FROM chat.messages
            WHERE room_id = ? AND bucket = ? AND message_id > ?
            ORDER BY message_id DESC
        """)

        # Select messages after a specific message
        self.select_messages_after_ps: PreparedStatement = self.session.prepare("""
            SELECT room_id, bucket, message_id, author_id, content, status, created_at, updated_at
            FROM chat.messages
            WHERE room_id = ? AND bucket = ? AND message_id < ?
            ORDER BY message_id DESC
        """)

        # Update message content and status
        self.update_message_content_ps: PreparedStatement = self.session.prepare("""
            UPDATE chat.messages
            SET content = ?, status = ?, updated_at = ?
            WHERE room_id = ? AND bucket = ? AND message_id = ?
        """)

        # Delete message
        self.delete_message_ps: PreparedStatement = self.session.prepare("""
            DELETE FROM chat.messages
            WHERE room_id = ? AND bucket = ? AND message_id = ?
        """)

        # Insert user message status
        self.insert_user_message_status_ps: PreparedStatement = self.session.prepare("""
            INSERT INTO chat.user_message_status (
                user_id, room_id, message_id, delivered_at, seen_at
            ) VALUES (?, ?, ?, ?, ?)
        """)

        # Select user message status
        self.select_user_message_status_ps: PreparedStatement = self.session.prepare("""
            SELECT user_id, room_id, message_id, delivered_at, seen_at
            FROM chat.user_message_status
            WHERE user_id = ? AND room_id = ? AND message_id = ?
        """)

        # Update user message status (delivered_at and seen_at)
        self.update_user_message_status_ps: PreparedStatement = self.session.prepare("""
            UPDATE chat.user_message_status
            SET delivered_at = ?, seen_at = ?
            WHERE user_id = ? AND room_id = ? AND message_id = ?
        """)

        # Delete user message status
        self.delete_user_message_status_ps: PreparedStatement = self.session.prepare("""
            DELETE FROM chat.user_message_status
            WHERE user_id = ? AND room_id = ? AND message_id = ?
        """)

    async def save_message(self, data: MessageCreate) -> MessageOut:
        """Insert a new message"""
        params = (
            data.room_id,
            data.bucket,
            data.message_id,
            data.author_id,
            data.content,
            data.status,
            data.created_at or datetime.now(),
            data.updated_at or datetime.now(),
        )
        future = self.session.execute_async(self.insert_message_ps, params)
        await future.result
        return MessageOut(**data.model_dump())

    async def list_messages(
        self,
        room_id: UUID,
        before: UUID | None = None,
        after: UUID | None = None,
        limit: int = 10,
    ):
        before = UUID("6b3998c6-8278-11f0-9da2-0242ac120009")
        if before is None and after is None:
            raise ValueError("Either 'before' or 'after' must be provided")

        if before is not None and after is not None:
            raise ValueError("Only one of 'before' or 'after' should be provided")

        if before is not None:
            future = self.session.execute_async(
                self.get_messages_before_ps, (room_id, before, limit)
            )
        else:
            future = self.session.execute_async(
                self.get_messages_after_ps, (room_id, after, limit)
            )

        result = await await_response_future(future)
        return list(result)

    async def update_message(
        self, room_id: UUID, message_id: UUID, content: str, updated_at: datetime
    ):
        future = self.session.execute_async(
            self.update_message_ps, (content, updated_at, room_id, message_id)
        )
        await await_response_future(future)

    async def update_status(
        self,
        message_id: UUID,
        user_id: UUID,
        status: int,
        delivered_at: Optional[datetime] = None,
        seen_at: Optional[datetime] = None,
    ):
        future = self.session.execute_async(
            self.update_status_ps, (message_id, user_id, status, delivered_at, seen_at)
        )
        await await_response_future(future)

    async def get_status(self, message_id: UUID, user_id: UUID):
        return await await_response_future(
            self.session.execute_async(self.get_status_ps, (message_id, user_id))
        )


async def message_repo_factory() -> MessageRepository:
    async with get_session() as session:
        return MessageRepository(session)
