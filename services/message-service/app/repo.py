from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.connection import setup
from cassandra.cqlengine import connection
from app.models import Message, MessageUserStatus


class MessageRepository:
    def __init__(self, keyspace="chat", contact_points=["127.0.0.1"]):
        self.keyspace = keyspace
        self.contact_points = contact_points
        self._connect()

    def _connect(self):
        setup(self.contact_points, self.keyspace, protocol_version=4)
        sync_table(Message)
        sync_table(MessageUserStatus)

    async def save_message(
        self, message_id, room_id: str, sender_id: str, content: str, timestamp
    ) -> dict:
        message = Message.create(
            message_id=message_id,
            room_id=room_id,
            sender_id=sender_id,
            content=content,
            timestamp=timestamp,
            media_ids=[],
        )
        return {
            "message_id": str(message.message_id),
            "room_id": message.room_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
        }

    async def get_recent_messages(self, room_id: str, limit: int = 50) -> list:
        query = Message.objects(room_id=room_id).limit(limit).all()
        return [
            {
                "message_id": str(row.message_id),
                "sender_id": row.sender_id,
                "content": row.content,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in query
        ]

    def close(self):
        connection.unregister_connection("default")
