import uuid
from typing import Optional, Sequence

import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from app.database import Database
from app.models import Room, RoomMember


class RoomRepository:
    def __init__(self, db: Database):
        self.db = db

    # --- Rooms ---
    async def create_room(
        self, type_: str, name: str, alias: Optional[str] = None, description: Optional[str] = None
    ) -> Room:
        async with self.db.get_session() as session:
            room = Room(
                type=type_,
                name=name,
                alias=alias,
                description=description,
            )
            session.add(room)
            await session.flush()
            return room

    async def get_or_create_dm(self, user1_id: str, user2_id: str) -> Room:
        u1, u2 = sorted([user1_id, user2_id])

        # Create deterministic room_id from both user ids
        room_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{u1}:{u2}")

        async with self.db.get_session() as session:
            stmt = sa.select(Room).where(Room.room_id == room_id, Room.type == "dm")
            result = await session.execute(stmt)
            room = result.scalars().first()

            if room:
                return room

            room = Room(
                room_id=room_id,
                type="dm",
                name="",
                alias="",
                description="",
            )
            session.add(room)
            await session.flush()

            session.add_all(
                [
                    RoomMember(room_id=room.room_id, user_id=u1),
                    RoomMember(room_id=room.room_id, user_id=u2),
                ]
            )
            await session.flush()

            return room

    async def get_room(self, room_id: uuid.UUID) -> Optional[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room).where(Room.room_id == room_id).options(
                selectinload(Room.members)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_room_by_alias(self, alias: str) -> Optional[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room).where(Room.alias == alias)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_rooms(self) -> Sequence[Room]:
        async with self.db.get_session() as session:
            stmt = sa.select(Room)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def delete_room(self, room_id: uuid.UUID) -> None:
        async with self.db.get_session() as session:
            stmt = sa.delete(Room).where(Room.room_id == room_id)
            await session.execute(stmt)

    # --- Members ---
    async def add_member(self, room_id: uuid.UUID, user_id: str) -> RoomMember:
        async with self.db.get_session() as session:
            member = RoomMember(room_id=room_id, user_id=user_id)
            session.add(member)
            await session.flush()
            return member

    async def remove_member(self, room_id: uuid.UUID, user_id: str) -> None:
        async with self.db.get_session() as session:
            stmt = sa.delete(RoomMember).where(
                RoomMember.room_id == room_id, RoomMember.user_id == user_id
            )
            await session.execute(stmt)

    async def is_member(self, room_id: uuid.UUID, user_id: str) -> bool:
        async with self.db.get_session() as session:
            stmt = sa.select(RoomMember).where(
                RoomMember.room_id == room_id, RoomMember.user_id == user_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def list_members(self, room_id: uuid.UUID) -> Sequence[RoomMember]:
        async with self.db.get_session() as session:
            stmt = sa.select(RoomMember).where(RoomMember.room_id == room_id)
            result = await session.execute(stmt)
            return result.scalars().all()
