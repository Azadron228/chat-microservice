from datetime import datetime
import json
import uuid
from nats.aio.client import Client as NATS
from app.repo import MessageRepository
nc = NATS()

async def connect_nats():
    await nc.connect("nats://localhost:4222")

async def disconnect_nats():
    await nc.close()

async def nats_message_handler(msg):
    repo = MessageRepository()
    data = json.loads(msg.data.decode())
    print(f"Received message: {data}")

    message = await repo.save_message(
        message_id=uuid.UUID(data["uuid"]),
        room_id=data["room_id"],
        sender_id=data["sender_id"],
        content=data["content"],
        timestamp=datetime.now(),
    )
    print(f"Message saved: {message}")