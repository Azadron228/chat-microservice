from app.core.jsonrpc.dispatcher import jsonrpc
from app.core.messaging.factory import broker
from app.domain.chat.service import add_client_to_room
from app.core.messaging.handlers.chat import subscribe_to_room


@jsonrpc("hello")
async def hello(user):
    return user

@jsonrpc("chat.join_room")
async def join_room(websocket, room_id):
    add_client_to_room(room_id, websocket)

    await subscribe_to_room(room_id=f"room.{room_id}")

    return {
        "room_id": room_id
    }

@jsonrpc("chat.send_message")
async def handle_send_message(user:dict, room_id:str, content: str):

    await broker.publish(f"room.{room_id}.message.to_save", {
        "type": "message",
        "content": content,
        "room_id": room_id,
        "user_id": user["name"]
    })


@jsonrpc("chat.get_messages")
async def get_messages():
    ...