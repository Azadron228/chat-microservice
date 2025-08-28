import logging
import asyncio
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

        self.user_rooms: Dict[str, Set[str]] = {}
        self.room_users: Dict[str, Set[str]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket
        user_rooms = await self.fetch_user_rooms(user_id)
        self.user_rooms[user_id] = user_rooms

        for room_id in user_rooms:
            if room_id not in self.room_users:
                self.room_users[room_id] = set()
            self.room_users[room_id].add(user_id)

        logger.info(f"User {user_id} connected. Total: {len(self.connections)}")

    async def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)
        for users in self.room_users.values():
            users.discard(user_id)
        logger.info(f"User {user_id} disconnected. Total: {len(self.connections)}")

    async def connect_room(self, user_id: str, room_id: str):
        if user_id not in self.connections:
            raise ValueError(f"User {user_id} not connected")
        self.room_users.setdefault(room_id, set()).add(user_id)
        logger.info(f"User {user_id} joined room {room_id}")

    async def disconnect_room(self, user_id: str, room_id: str):
        if room_id in self.room_users:
            self.room_users[room_id].discard(user_id)
        logger.info(f"User {user_id} left room {room_id}")

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

    async def broadcast_room(self, room_id: str, message: dict):
        user_ids = self.room_users.get(room_id, set())
        await self.broadcast(user_ids, message)

    async def broadcast_all(self, message: dict):
        await self.broadcast(set(self.connections.keys()), message)


connection_manager = ConnectionManager()
