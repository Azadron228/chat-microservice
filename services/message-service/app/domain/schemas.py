from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    room_id: UUID
    bucket: int
    author_id: UUID
    content: str
    status: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageCreate(MessageBase):
    message_id: UUID


class MessageUpdate(BaseModel):
    content: str
    status: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class MessageOut(MessageBase):
    message_id: UUID


class UserMessageStatusBase(BaseModel):
    user_id: UUID
    room_id: UUID
    message_id: UUID


class UserMessageStatusCreate(UserMessageStatusBase):
    delivered_at: Optional[datetime] = None
    seen_at: Optional[datetime] = None


class UserMessageStatusUpdate(BaseModel):
    delivered_at: Optional[datetime] = None
    seen_at: Optional[datetime] = None


class UserMessageStatusOut(UserMessageStatusBase):
    delivered_at: Optional[datetime]
    seen_at: Optional[datetime]
