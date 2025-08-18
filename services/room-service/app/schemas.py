import uuid
from pydantic import BaseModel
from typing import Optional, List


class RoomCreate(BaseModel):
    type: str
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None


class RoomOut(BaseModel):
    room_id: uuid.UUID
    type: str
    name: str
    alias: Optional[str]
    description: Optional[str]

    class Config:
        from_atributes = True


class MemberAdd(BaseModel):
    user_id: str


class RoomMemberOut(BaseModel):
    room_id: uuid.UUID
    user_id: str

    class Config:
        from_atributes = True
