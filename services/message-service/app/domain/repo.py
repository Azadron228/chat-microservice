from cassandra.query import PreparedStatement
from uuid import UUID
from datetime import datetime


class MessageRepository:
    def __init__(self, session):
        self.session = session
        self.insert_message_ps: PreparedStatement = session.prepare("""
            INSERT INTO chat.messages (
                room_id, created_at, updated_at, message_id,
                sender_id, content, media_ids, reply_to,
                quote, is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, false)
        """)

        self.get_recent_messages_ps: PreparedStatement = session.prepare("""
            SELECT * FROM chat.messages
            WHERE room_id = ?
            ORDER BY message_id DESC
            LIMIT ?
        """)

        self.get_message_ps: PreparedStatement = session.prepare("""
            SELECT * FROM chat.messages
            WHERE room_id = ? AND message_id = ?
        """)

        self.update_message_ps: PreparedStatement = session.prepare("""
            UPDATE chat.messages
            SET content = ?, updated_at = ?
            WHERE room_id = ? AND message_id = ?
        """)

        self.mark_deleted_ps: PreparedStatement = session.prepare("""
            UPDATE chat.messages
            SET is_deleted = true, updated_at = ?
            WHERE room_id = ? AND message_id = ?
        """)

        self.update_status_ps: PreparedStatement = session.prepare("""
            INSERT INTO chat.message_user_status (
                message_id, user_id, status, delivered_at, seen_at
            ) VALUES (?, ?, ?, ?, ?)
        """)

        self.get_status_ps: PreparedStatement = session.prepare("""
            SELECT * FROM chat.message_user_status
            WHERE message_id = ? AND user_id = ?
        """)

    async def save_message(
        self,
        message_id: UUID,
        room_id: str,
        sender_id: str,
        content: str,
        timestamp: datetime,
        media_ids=None,
        reply_to=None,
        quote=None,
    ):
        await self.session.execute_async(
            self.insert_message_ps,
            (
                room_id,
                timestamp,
                timestamp,
                message_id,
                sender_id,
                content,
                media_ids or [],
                reply_to,
                quote,
            ),
        )

    async def get_recent_messages(self, room_id: str, limit: int = 50):
        rows = await self.session.execute_async(
            self.get_recent_messages_ps, (room_id, limit)
        )
        return list(rows)

    async def get_message(self, room_id: str, message_id: UUID):
        row = await self.session.execute_async(
            self.get_message_ps, (room_id, message_id)
        )
        return row.one()

    async def update_message(self, room_id: str, message_id: UUID, content: str):
        await self.session.execute_async(
            self.update_message_ps, (content, datetime.now(), room_id, message_id)
        )

    async def mark_as_deleted(self, room_id: str, message_id: UUID):
        await self.session.execute_async(
            self.mark_deleted_ps, (datetime.datetime.now(), room_id, message_id)
        )

    async def update_status(self, message_id: UUID, user_id: str, status: int):
        now = datetime.now()
        delivered_at = now if status == 0 else None
        seen_at = now if status == 1 else None
        await self.session.execute_async(
            self.update_status_ps, (message_id, user_id, status, delivered_at, seen_at)
        )

    async def get_status(self, message_id: UUID, user_id: str):
        row = await self.session.execute_async(
            self.get_status_ps, (message_id, user_id)
        )
        return row.one()
