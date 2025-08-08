
from datetime import datetime
import uuid
from app.core.rpc import rpc_method
from app.models.chat import JoinRoomParams, SendMessageParams
from app.models.rpc import RPCResponse
from app.services.rooms import add_client_to_room
from app.services.chats import ChatService
from app.core.nats import create_nats_message_handler, nc, publish_to_room
from app.models.rpc import RPCRequest

from fastapi import WebSocket
from app.models.rpc import RPCRequest, RPCResponse

async def handle_join_room(websocket: WebSocket, request: RPCRequest) -> RPCResponse:
    p = JoinRoomParams(**request.params)
    
    await websocket.send_text(f"joined {p.room_id}")
    return RPCResponse(result={"status": "ok"}, id=request.id)

@rpc_method("join_room")
async def handle_join_room(websocket: WebSocket, request: RPCRequest) -> RPCResponse:
    p = JoinRoomParams(**request.params)

    add_client_to_room(p.room_id, websocket)

    nats_message_handler = await create_nats_message_handler(websocket)
    # Subscribe to room topic
    await nc.subscribe(f"room.{p.room_id}", cb=nats_message_handler)

    # Notify others
    await publish_to_room(p.room_id, {
        "type": "system",
        "room_id": p.room_id,
    })

    return RPCResponse(
        result={"message": f"Joined room {p.room_id}"},
        id=request.id
    )


@rpc_method("send_message")
async def handle_send_message(websocket: WebSocket, request: RPCRequest) -> RPCResponse:
    p = SendMessageParams(**request.params)

    await publish_to_room(p.room_id, {
        "type": "message",
        "content": p.content,
        "room_id": p.room_id,
    })

    chat_service = ChatService()

    r = await chat_service.save_message(
        room_id=1,
        sender_id=1,
        content="Hello from chat service!",
    )
    if r:
        return RPCResponse(
            result={"message": "Message sent"},
            id=request.id
        )
    else:
        # Handle error case
        return RPCResponse(
            error={"code": 500, "message": "Failed to send message"},
            id=request.id
        )



@rpc_method("get_messages")
async def handle_get_messages(websocket, request_id: str) -> RPCResponse:
    return RPCResponse(
        result={"message": "This method is not implemented yet."},
        id=request_id
    )
