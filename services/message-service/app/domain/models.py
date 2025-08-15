
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from protos import message_pb2

@dataclass
class Message:
    message_id: UUID
    room_id: UUID
    author_id: UUID
    content: str
    status: Optional[str] = None

    def to_proto(self) -> message_pb2.MessageResponse:
        return message_pb2.MessageResponse(
            message_id=str(self.message_id),
            room_id=str(self.room_id),
            author_id=str(self.author_id),
            content=self.content,
        )