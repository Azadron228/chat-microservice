import uuid
import grpc
from app.core.jsonrpc.dispatcher import JsonRpcRouter
from app.core.messaging.factory import broker
from protos import message_pb2 as message_pb2
from protos import message_pb2_grpc as message_pb2_grpc
import logging
from app.core.config import settings
from app.domain.chat.room_service import room_service
from app.core.connection_manager import connection_manager

logger = logging.getLogger(__name__)

jsonrpc = JsonRpcRouter()

@jsonrpc.method("hello")
async def hello(user_id: str):
    return f"Hello, your user_id: {user_id}"

@jsonrpc.method("chat.join_room")
async def join_room(websocket, user_id: str, room_id: str):
    connection_manager.join_room(user_id, room_id=room_id, websocket=websocket)

    return {
        "status": "joined",
        "room_id": room_id
    }

@jsonrpc.method("chat.send_message")
async def handle_send_message(user_id: str, room_id:str, content: str):
    room_id = str(uuid.uuid1())
    await broker.publish("chat.messages.message.to_save", {
        "content": content,
        "room_id": room_id,
        "author_id": user_id
    })


@jsonrpc.method("chat.get_messages")
async def get_messages(room_id:str):
    async with grpc.aio.insecure_channel("message.local:50051") as channel:
        stub = message_pb2_grpc.MessageServiceStub(channel)

        request = message_pb2.ListMessagesRequest(
            room_id=room_id,
            limit=10
        )

        try:
            response = await stub.ListMessages(request)
            logger.info(f"Got messages: {len(response.messages)}")

            # Convert protobuf messages to plain dicts
            messages_list = []
            for msg in response.messages:
                messages_list.append({
                    "message_id": msg.message_id,
                    "room_id": msg.room_id,
                    "author_id": msg.author_id,
                    "content": msg.content,
                    "status": msg.status,
                })

            return messages_list

        except grpc.aio.AioRpcError as e:
            return {
                "error": {
                    "code": e.code().name,
                    "details": e.details()
                }
            }

