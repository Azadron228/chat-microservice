from pydantic import BaseModel, Field

class JoinRoomParams(BaseModel):
    room_id: str = Field(..., description="ID of the room to join")

class SendMessageParams(BaseModel):
    sender_id: str = Field(..., description="ID of the user sending the message")
    room_id: str = Field(..., description="Room to send the message to")
    content: str = Field(..., description="Message content")
