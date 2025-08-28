from dataclasses import dataclass
import uuid
from typing import Optional, Sequence

import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.database import Database
from app.models import Room, RoomMember, RoomType


@dataclass
class RoomCreate:
    type: RoomType
    name: Optional[str] = None
    alias: Optional[str] = None
    description: Optional[str] = None
    members: Optional[list[str]] = None  # user_ids


@dataclass
class RoomUpdateLastMessage:
    message_id: int
    preview: str
    created_at: datetime
    author_id: str

@dataclass
class MemberAdd:
    room_id: uuid.UUID
    user_id: str


class RoomRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_dm_id(self, user1_id: str, user2_id: str) -> uuid.UUID:
        u1, u2 = sorted([user1_id, user2_id])
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"{u1}:{u2}")

    # --- Rooms ---
    async def list_rooms(self, user_id: Optional[str] = None) -> Sequence[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room)
            if user_id:
                stmt = stmt.join(RoomMember).where(RoomMember.user_id == user_id)

            result = await session.execute(stmt.options(selectinload(Room.members)))
            return result.scalars().all()
    
    async def create_room(self, data: RoomCreate) -> Room:
        async with self.db.get_session() as session:
            if data.type == RoomType.DIRECT and data.members and len(data.members) == 2:
                data.room_id = self.get_dm_id(data.members[0], data.members[1])
            
            room = Room(
                room_id=data.room_id,
                type=data.type,
                name=data.name,
                alias=data.alias,
                description=data.description,
            )
            session.add(room)
            await session.flush()

            if data.members:
                session.add_all(
                    [
                        RoomMember(room_id=room.room_id, user_id=user_id, last_read_message_id=0)
                        for user_id in data.members
                    ]
                )
                await session.flush()

            return room

    async def get_room(
        self, room_id: uuid.UUID
    ) -> Optional[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room).where(Room.room_id == room_id)

            result = await session.execute(stmt.options(selectinload(Room.members)))
            return result.scalar_one_or_none()

    async def get_or_create_dm(self, user1_id: str, user2_id: str) -> Room:
        room_id = self.get_dm_id(user1_id, user2_id)
        room = await self.get_room(room_id)
        if room:
            return room

        return await self.create_room(
            RoomCreate(type=RoomType.DIRECT, members=[user1_id, user2_id])
        )

    async def update_last_message(
        self, room_id: uuid.UUID, data: RoomUpdateLastMessage
    ) -> None:
        async with self.db.get_session() as session:
            stmt = (
                sa.update(Room)
                .where(Room.room_id == room_id)
                .values(
                    last_message_id=data.message_id,
                    last_message_preview=data.preview[:255],
                    last_message_at=data.created_at,
                    last_message_sender_id=data.author_id,
                )
            )
            await session.execute(stmt)

    # --- Members ---
    async def add_member(self, data: MemberAdd) -> RoomMember:
        async with self.db.get_session() as session:
            member = RoomMember(**data.dict())
            session.add(member)
            await session.flush()
            return member

    async def remove_member(self, room_id: uuid.UUID, user_id: str) -> None:
        async with self.db.get_session() as session:
            stmt = sa.delete(RoomMember).where(
                RoomMember.room_id == room_id, RoomMember.user_id == user_id
            )
            await session.execute(stmt)

    async def list_members(self, room_id: uuid.UUID) -> Sequence[RoomMember]:
        async with self.db.get_session() as session:
            stmt = sa.select(RoomMember).where(RoomMember.room_id == room_id)
            result = await session.execute(stmt)
            return result.scalars().all()