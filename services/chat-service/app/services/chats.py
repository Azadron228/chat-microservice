import datetime
import json
import uuid
from fastapi import WebSocket
from app.core.nats import create_nats_message_handler, nc, publish_to_room
from app.services.rooms import add_client_to_room
from app.models.chat import JoinRoomParams


class ChatService:
    def __init__(self):
        pass

    async def save_message(self, room_id, sender_id, content):

        await nc.publish(f"message.created", json.dumps({
            "type": "message",
            "uuid": str(uuid.uuid1()),
            "content": content,
            "sender_id": sender_id,
            "room_id": room_id,
        }).encode('utf-8'))


        return True