from dataclasses import dataclass
import uuid
from typing import Optional, Sequence

import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.database import Database
from app.models import Room, RoomMember, RoomType


class RoomRepository:
    def __init__(self, db: Database):
        self.db = db

    async def list_rooms(self, user_id: Optional[str] = None) -> Sequence[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room)
            if user_id:
                stmt = stmt.join(RoomMember).where(RoomMember.user_id == user_id)

            result = await session.execute(stmt.options(selectinload(Room.members)))
            return result.scalars().all()

    async def create_room(self, room_id, data) -> Room:
        async with self.db.get_session() as session:
            room = Room(
                room_id=room_id,
                type=data.type,
                name=data.name,
                alias=data.alias,
                description=data.description,
            )
            session.add(room)
            await session.flush()

            if data.members:
                members = set(data.members)
                session.add_all(
                    [
                        RoomMember(room_id=room.room_id, user_id=uid)
                        for uid in members
                    ]
                )
                await session.flush()

            return room

    async def get_room(self, room_id: uuid.UUID) -> Optional[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room).where(Room.room_id == room_id)

            result = await session.execute(stmt.options(selectinload(Room.members)))
            return result.scalar_one_or_none()

    async def update_room(self, room_id: uuid.UUID, data) -> Optional[Room]:
        async with self.db.get_session() as session:
            stmt = (
                sa.update(Room)
                .where(Room.room_id == room_id)
                .values(**data.dict(exclude_none=True))
            )
            await session.execute(stmt)

    async def update_last_message(self, room_id: uuid.UUID, data) -> None:
        async with self.db.get_session() as session:
            stmt = sa.update(Room).where(Room.room_id == room_id).values(**data.dict())
            await session.execute(stmt)

    async def add_member(self, data) -> RoomMember:
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
