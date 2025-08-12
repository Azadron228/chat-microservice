import grpc
import uuid
from app.protos import message_pb2, message_pb2_grpc
from app.models import Message

class MessageService(message_pb2_grpc.MessageServiceServicer):
    def SendMessage(self, request, context):
        message_id = uuid.uuid4()
        msg = Message.create(
            room_id=request.room_id,
            sender_id=request.sender_id,
            message_id=message_id,
            content=request.content,
            media_ids=request.media_ids,
            reply_to=request.reply_to or None,
            quote=request.quote or None,
        )
        return message_pb2.SendMessageResponse(
            message_id=str(msg.message_id),
            timestamp=grpc.timestamp_pb2.Timestamp(seconds=int(msg.timestamp.timestamp()))
        )

    def GetMessageStatus(self, request, context):

        ...
        return message_pb2.GetMessageStatusResponse(...)

async def serve():
    server = grpc.aio.server()
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("MessageService gRPC server running on port 50051")
    await server.wait_for_termination()