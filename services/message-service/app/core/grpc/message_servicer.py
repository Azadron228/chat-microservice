import grpc
from uuid import UUID
from typing import List
from google.protobuf.json_format import MessageToDict, ParseDict
import message_pb2
import message_pb2_grpc
from app.domain.service import MessageService

class MessageServicer(message_pb2_grpc.MessageServiceServicer):
    def __init__(self, message_service: MessageService):
        self.message_service = message_service

    async def CreateMessage(self, request, context):
        try:
            media_ids = [UUID(mid) for mid in request.media_ids] if request.media_ids else None
            result = await self.message_service.create_message(
                room_id=UUID(request.room_id),
                author_id=UUID(request.author_id),
                content=request.content,
                media_ids=media_ids
            )
            return message_pb2.MessageResponse(**result)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating message: {str(e)}")
            raise

    async def ListMessages(self, request, context):
        try:
            messages = await self.message_service.list_messages(
                room_id=UUID(request.room_id),
                limit=request.limit if request.limit > 0 else 50
            )
            return message_pb2.ListMessagesResponse(messages=[
                message_pb2.MessageResponse(**msg) for msg in messages
            ])
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing messages: {str(e)}")
            raise

    async def UpdateMessage(self, request, context):
        try:
            result = await self.message_service.update_message(
                room_id=UUID(request.room_id),
                message_id=UUID(request.message_id),
                content=request.content
            )
            return message_pb2.UpdateMessageResponse(**result)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating message: {str(e)}")
            raise

    async def UpdateStatus(self, request, context):
        try:
            result = await self.message_service.update_status(
                message_id=UUID(request.message_id),
                user_id=UUID(request.user_id),
                status=request.status
            )
            return message_pb2.UpdateStatusResponse(**result)
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating status: {str(e)}")
            raise