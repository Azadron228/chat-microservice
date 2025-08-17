from cassandra.query import PreparedStatement
from uuid import UUID
from datetime import datetime
from app.core.casssandra import await_response_future, get_session


import uuid
from datetime import datetime
from cassandra.cluster import Session, PreparedStatement
from typing import List, Optional
from uuid import UUID


class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

        # Insert message
        self.insert_message_ps: PreparedStatement = session.prepare("""
            INSERT INTO chat.messages (
                room_id, message_id, author_id,
                content, media_ids, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """)

        # Update message content
        self.update_message_ps: PreparedStatement = session.prepare("""
            UPDATE chat.messages
            SET content = ?, updated_at = ?
            WHERE room_id = ? AND message_id = ?
        """)

       # Before (older messages)
        self.get_messages_before_ps: PreparedStatement = session.prepare("""
            SELECT *
            FROM chat.messages
            WHERE room_id = ?
            AND message_id < ?
            ORDER BY message_id DESC
            LIMIT ?
        """)

        # After (newer messages)
        self.get_messages_after_ps: PreparedStatement = session.prepare("""
            SELECT *
            FROM chat.messages
            WHERE room_id = ?
            AND message_id > ?
            ORDER BY message_id DESC
            LIMIT ?
        """)

        # Insert or update user status
        self.update_status_ps: PreparedStatement = session.prepare("""
            INSERT INTO chat.message_user_status (
                message_id, user_id, status, delivered_at, seen_at
            ) VALUES (?, ?, ?, ?, ?)
        """)

        # Get user status
        self.get_status_ps: PreparedStatement = session.prepare("""
            SELECT * FROM chat.message_user_status
            WHERE message_id = ? AND user_id = ?
        """)

    async def save_message(
        self,
        room_id: UUID,
        message_id: UUID,
        author_id: UUID,
        content: str,
        media_ids: Optional[List[UUID]],
        timestamp: datetime
    ):
        future = self.session.execute_async(
            self.insert_message_ps,
            (
                room_id,
                message_id,
                author_id,
                content,
                media_ids or [],
                timestamp,
                timestamp
            )
        )
        await await_response_future(future)

    async def list_messages(
        self,
        room_id: UUID,
        before: UUID | None = None,
        after: UUID | None = None,
        limit: int = 10,
    ):
        if before is None and after is None:
            raise ValueError("Either 'before' or 'after' must be provided")

        if before is not None and after is not None:
            raise ValueError("Only one of 'before' or 'after' should be provided")

        if before is not None:
            future = self.session.execute_async(
                self.get_messages_before_ps,
                (room_id, before, limit)
            )
        else:
            future = self.session.execute_async(
                self.get_messages_after_ps,
                (room_id, after, limit)
            )

        result = await await_response_future(future)
        return list(result)
    

    async def update_message(
        self,
        room_id: UUID,
        message_id: UUID,
        content: str,
        updated_at: datetime
    ):
        future = self.session.execute_async(
            self.update_message_ps,
            (
                content,
                updated_at,
                room_id,
                message_id
            )
        )
        await await_response_future(future)

    async def update_status(
        self,
        message_id: UUID,
        user_id: UUID,
        status: int,
        delivered_at: Optional[datetime] = None,
        seen_at: Optional[datetime] = None
    ):
        future = self.session.execute_async(
            self.update_status_ps,
            (
                message_id,
                user_id,
                status,
                delivered_at,
                seen_at
            )
        )
        await await_response_future(future)

    async def get_status(self, message_id: UUID, user_id: UUID):
        return await await_response_future(
            self.session.execute_async(self.get_status_ps, (message_id, user_id))
        )

async def message_repo_factory() -> MessageRepository:
    async with get_session() as session:
        return MessageRepository(session)