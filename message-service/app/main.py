import json
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from app.core.nats import connect_nats, disconnect_nats, nc

from uuid import uuid4
from datetime import datetime


class MessageRepository:
    def __init__(self, keyspace: str = "chat", contact_points: list = ["127.0.0.1"]):
        self.cluster = Cluster(contact_points)
        self.session = self.cluster.connect()
        self.session.set_keyspace(keyspace)
        self._prepare_statements()

    def _prepare_statements(self):
        self.insert_stmt = self.session.prepare("""
            INSERT INTO messages (room_id, message_id, sender_id, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """)

        self.select_stmt = self.session.prepare("""
            SELECT message_id, sender_id, content, timestamp
            FROM messages
            WHERE room_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """)

    async def save_message(self, message_id, room_id: str, sender_id: str, content: str, timestamp) -> dict:

        await self.session.execute_async(self.insert_stmt, (room_id, message_id, sender_id, content, timestamp))

        return {
            "message_id": str(message_id),
            "room_id": room_id,
            "sender_id": sender_id,
            "content": content,
            "timestamp": timestamp.isoformat()
        }

    def get_recent_messages(self, room_id: str, limit: int = 50) -> list:
        rows = self.session.execute(self.select_stmt, (room_id, limit))
        return [
            {
                "message_id": str(row.message_id),
                "sender_id": row.sender_id,
                "content": row.content,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in rows
        ]

    def close(self):
        self.cluster.shutdown()


async def nats_message_handler(msg):
    data = json.loads(msg.data.decode())
    print(f"Received message: {data}")

    message = await repo.save_message(
        message_id=data["uuid"],
        room_id=data["room_id"],
        sender_id=data["sender_id"],
        content=data["content"],
        timestamp=datetime.now(),
    )
    print(f"Message saved: {message}")

async def main():
    global repo
    repo = MessageRepository()

    await connect_nats()

    # Subscribe to NATS messages
    await nc.subscribe("message.created", cb=nats_message_handler)

    print("NATS connected and message handler set up.")

    while True:
        try:
            await asyncio.sleep(1)  # Keep the event loop running
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    # repo = MessageRepository()

    # await connect_nats()

    # nc.subscribe("messages.created", cb=nats_message_handler)
    

    # # Save a message
    # # message = repo.save_message("room123", "user456", "Hello from Cassandra!")
    # # print("Saved:", message)

    # # Get recent messages
    # # messages = repo.get_recent_messages("room123")
    # # print("Recent messages:")
    # # for msg in messages:
    #     # print(msg)

    # repo.close()
    # disconnect_nats()
