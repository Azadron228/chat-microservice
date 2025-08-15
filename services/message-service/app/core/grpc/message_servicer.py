import grpc
from uuid import UUID
from typing import List
from google.protobuf.json_format import MessageToDict, ParseDict
from app.domain.service import MessageService
from app.core.grpc.gen import message_pb2_grpc, message_pb2
from app.core.casssandra import get_session
from app.domain.repo import MessageRepository
from app.core.messaging.factory import broker
class MessageServicer(message_pb2_grpc.MessageServiceServicer):
    def __init__(self, message_service: MessageService):
        self.message_service = message_service

    async def ListMessages(self, request, context):
        try:
            async with get_session() as session:
                service = MessageService(repo=MessageRepository(session), broker=broker)
                messages = await service.list_messages(
                    room_id=UUID(request.room_id),
                    limit=request.limit if request.limit > 0 else 50
                )
                return message_pb2.ListMessagesResponse(messages=[
                    message_pb2.MessageResponse(**{k: v for k, v in msg.items() if k in {
                        "message_id", "room_id", "author_id", "content", "status"
                    }})
                    for msg in messages
                ])
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing messages: {str(e)}")
            raise

    async def GetMessageStatus(self, request, context):
        try:
            message = await self.message_service.get_message_status(
                message_id=request.message_id
            )
            return message_pb2.MessagesResponse(messages=[
                message_pb2.MessageResponse(message)
            ])
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting message status: {str(e)}")
            raise