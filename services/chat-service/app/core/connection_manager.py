import logging
from typing import Dict

logger = logging.getLogger(__name__)
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, object] = {}

        self.rooms: Dict[str, set[str]] = {}

    def connect(self, user_id: str, websocket):
        logger.info(f"User {user_id} connected")
        logger.info(f"Current connections: {list(self.connections.keys())}")
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

    def join_room(self, user_id: str, room_id: str, websocket):
        self.connect(user_id, websocket)
        self.rooms.setdefault(room_id, set()).add(user_id)

    def is_online(self, user_id: str) -> bool:
        return user_id in self.connections

    async def send_to_user(self, user_id: str, message: dict):
        logger.info(f"Sending message to user {user_id}")
        ws = self.connections.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, user_ids: set[str], message: dict):
        logger.info(f"Broadcasting to {len(user_ids)} users")
        for uid in user_ids:
            await self.send_to_user(uid, message)

    async def broadcast_room(self, room_id: str, message: dict):
        user_ids = self.rooms.get(room_id, set())
        await self.broadcast(user_ids, message)

connection_manager = ConnectionManager()
