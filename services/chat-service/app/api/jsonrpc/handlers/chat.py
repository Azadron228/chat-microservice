import uuid
import grpc
from app.core.jsonrpc.dispatcher import jsonrpc
from app.core.messaging.factory import broker
from app.domain.chat.service import add_client_to_room
from app.core.messaging.handlers.chat import subscribe_to_room
from protos import message_pb2 as message_pb2
from protos import message_pb2_grpc as message_pb2_grpc
import logging
from app.core.config import settings
logger = logging.getLogger(__name__)

@jsonrpc("hello")
async def hello(user_id: str):
    return f"Hello, your user_id: {user_id}"

@jsonrpc("chat.join_room")
async def join_room(websocket):
    room_id = str(uuid.uuid1)
    add_client_to_room(room_id, websocket)

    return {
        "room_id": room_id
    }

@jsonrpc("chat.send_message")
async def handle_send_message(user_id: str, room_id:str, content: str):

    await broker.publish("chat.messages.message.to_save", {
        "content": content,
        "room_id": room_id,
        "author_id": user_id
    })


@jsonrpc("chat.get_messages")
async def get_messages(room_id:str):
    async with grpc.aio.insecure_channel(settings.MESSAGE_SERVICE_GRPC_URL) as channel:
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
                    # "timestamp": msg.timestamp.ToDatetime().isoformat()
                    # if msg.HasField("timestamp") else None
                })

            return messages_list

        except grpc.aio.AioRpcError as e:
            return {
                "error": {
                    "code": e.code().name,
                    "details": e.details()
                }
            }
