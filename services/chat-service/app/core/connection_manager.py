import logging
import asyncio
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

        # All user -> rooms mapping
        self.user_rooms: Dict[str, Set[str]] = {}

        # Active & inactive memberships
        self.active_room_users: Dict[str, Set[str]] = {}
        self.inactive_room_users: Dict[str, Set[str]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket
        user_rooms = await self.fetch_user_rooms(user_id)
        self.user_rooms[user_id] = user_rooms

        for room_id in user_rooms:
            self.inactive_room_users.setdefault(room_id, set()).add(user_id)

        logger.info(f"User {user_id} connected. Total: {len(self.connections)}")

    async def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)

        for room_id in self.active_room_users:
            self.active_room_users[room_id].discard(user_id)

        for room_id in self.inactive_room_users:
            self.inactive_room_users[room_id].discard(user_id)

        logger.info(f"User {user_id} disconnected. Total: {len(self.connections)}")

    async def connect_room(self, user_id: str, room_id: str):
        if user_id not in self.connections:
            raise ValueError(f"User {user_id} not connected")

        # Move user from inactive to active
        self.inactive_room_users.setdefault(room_id, set()).discard(user_id)
        self.active_room_users.setdefault(room_id, set()).add(user_id)

        logger.info(f"User {user_id} joined room {room_id} (active)")

    async def disconnect_room(self, user_id: str, room_id: str):
        if room_id in self.active_room_users:
            self.active_room_users[room_id].discard(user_id)
        self.inactive_room_users.setdefault(room_id, set()).add(user_id)

        logger.info(f"User {user_id} left room {room_id} (inactive)")

    async def send_to_user(self, user_id: str, message: dict):
        ws = self.connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast(self, user_ids: Set[str], message: dict):
        for uid in user_ids:
            await self.send_to_user(uid, message)

    async def send_to_active_users(self, room_id: str, message: dict):
        user_ids = self.active_room_users.get(room_id, set())
        await self.broadcast(user_ids, message)

    async def send_to_inactive_users(self, room_id: str, message: dict):
        user_ids = self.inactive_room_users.get(room_id, set())
        await self.broadcast(user_ids, message)

    async def broadcast_all(self, message: dict):
        await self.broadcast(set(self.connections.keys()), message)


connection_manager = ConnectionManager()
