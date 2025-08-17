from typing import Dict, Set
import uuid


class RoomService():
    def __init__(self):
        self.room_members: Dict[str, Set[str]] = {}

    def add_user_to_room(self, room_id: str, user_id: str):
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        self.room_members[room_id].add(user_id)

    def get_room_members(self, room_id: str) -> Set[str]:
        return self.room_members.get(room_id, set())

    def get_or_create_dm_room(self, user_id: str, target_user_id: str) -> str:
        room_id = str(uuid.uuid4())
        self.add_user_to_room(room_id, user_id)
        self.add_user_to_room(room_id, target_user_id)
        return room_id
    
room_service = RoomService()