from typing import List, Union
import uuid
from app.repo import RoomRepository
from app.schemas import DmRoomOut, RoomCreate, RoomOut, RoomUpdate, RoomUpdateLastMessage
from app.models import RoomType
from app.messaging.factory import broker


class RoomService:
    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository

    def get_dm_id(self, user1_id: str, user2_id: str) -> uuid.UUID:
        u1, u2 = sorted([user1_id, user2_id])
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"{u1}:{u2}")

    async def create_room(self, room_data):
        room_id = uuid.uuid4()
        return await self.room_repository.create_room(room_id, room_data)

    async def start_dm(self, user1_id, user2_id):
        room_id = self.get_dm_id(user1_id, user2_id)

        room = await self.room_repository.get_room(room_id)
        if room:
            return room

        data = RoomCreate(
            room_id=room_id, type=RoomType.DIRECT, members=[user1_id, user2_id]
        )

        return await self.room_repository.create_room(room_id, data)
    
    async def get_dm(self, user1_id, user2_id):
        room_id = self.get_dm_id(user1_id, user2_id)

        return await self.room_repository.get_room(room_id)

    async def get_room(self, room_id):
        return self.room_repository.get_room(room_id)

    async def update_room(self, room_id, room_data):
        return self.room_repository.update_room(room_id, room_data)

    async def update_last_message(self, room_id, data):
        data.preview = data.preview[:255]
        self.room_repository.update_last_message(room_id, data)
        broker.publish("room.message", data.dict())

    async def delete_room(self, room_id):
        return self.room_repository.delete_room(room_id)

    async def list_rooms(self, user_id):
        rooms = await self.room_repository.list_rooms(user_id)

        result: List[Union[RoomOut, DmRoomOut]] = []

        for room in rooms:
            if room.type == RoomType.DIRECT:
                other_member = next(
                    (m for m in room.members if m.user_id != user_id), None
                )
                result.append(DmRoomOut(
                    room_id=room.room_id,
                    type=room.type,
                    user_id=other_member.user_id if other_member else None,
                    last_message_id=room.last_message_id,
                    last_message_preview=room.last_message_preview,
                    last_message_at=room.last_message_at,
                    last_message_sender_id=room.last_message_sender_id
                ))
            else:
                result.append(RoomOut(
                    room_id=room.room_id,
                    type=room.type,
                    name=room.name,
                    alias=room.alias,
                    description=room.description,
                    last_message_id=room.last_message_id,
                    last_message_preview=room.last_message_preview,
                    last_message_at=room.last_message_at,
                    last_message_sender_id=room.last_message_sender_id
                ))

        return result
