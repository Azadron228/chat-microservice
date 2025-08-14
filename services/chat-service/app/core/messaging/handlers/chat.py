import json
import logging
from app.domain.chat.service import rooms,remove_client_from_all_rooms
from app.core.messaging.factory import broker

logger = logging.getLogger(__name__)

async def subscribe_to_room(room_id):
    async def subscribe_to_room_handler(data: dict):
        room_id = data.get("room_id")
        content = data.get("content")
        
        if not room_id or not content:
            return

        clients = rooms.get(room_id, set())
        
        for client in clients:
            try:
                await client.send_text(json.dumps({
                    "type": "message",
                    "room_id": room_id,
                    "content": content
                }))
            except Exception as e:
                # Remove disconnected clients
                remove_client_from_all_rooms(client)
    await broker.subscribe(room_id, handler=subscribe_to_room_handler)


async def to_broadcast_handler(msg):
    logger.info(f"Got message:{msg}")
    if not msg["room_id"]:
        return
    clients = rooms.get(msg["room_id"], set())
        
    for client in clients:
        try:
            await client.send_text(json.dumps({
                msg
            }))
        except Exception as e:
            # Remove disconnected clients
            remove_client_from_all_rooms(client)
