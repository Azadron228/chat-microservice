import uuid
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime
from app.models import RoomType


class RoomBase(BaseModel):
    room_id: uuid.UUID
    type: RoomType

    last_message_id: Optional[int] = None
    last_message_preview: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_sender_id: Optional[str] = None

    class Config:
        from_attributes = True


class RoomOut(RoomBase):
    name: Optional[str] = None
    alias: Optional[str] = None
    description: Optional[str] = None
    unread_count: Optional[int] = 0


class DmRoomOut(RoomBase):
    user_id: Optional[str] = None
    unread_count: Optional[int] = 0


class RoomCreate(BaseModel):
    type: RoomType = RoomType.GROUP
    name: Optional[str] = None
    alias: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[str]] = None


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    description: Optional[str] = None


class RoomUpdateLastMessage(BaseModel):
    message_id: int
    preview: str
    created_at: datetime
    author_id: str


class MemberAdd(BaseModel):
    room_id: uuid.UUID
    user_id: str
