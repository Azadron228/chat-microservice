import grpc
from uuid import UUID
from app.domain.service import message_service_factory
from protos import message_pb2, message_pb2_grpc


class MessageServicer(message_pb2_grpc.MessageServiceServicer):
    async def ListMessages(self, request, context):
        try:
            service = await message_service_factory()
            messages = await service.list_messages(
                room_id=UUID(request.room_id), limit=10
            )
            return message_pb2.ListMessagesResponse(
                messages=[msg.to_proto() for msg in messages]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing messages: {str(e)}")
            raise

    async def GetMessageStatus(self, request, context):
        try:
            message = await self.message_service.get_message_status(
                message_id=request.message_id
            )
            return message_pb2.MessagesResponse(
                messages=[message_pb2.MessageResponse(message)]
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid UUID format: {str(e)}")
            raise
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error getting message status: {str(e)}")
            raise
