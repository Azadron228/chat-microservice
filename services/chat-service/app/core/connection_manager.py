import logging
import asyncio
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # user_id -> websocket
        self.connections: Dict[str, WebSocket] = {}

        # room_id -> set of user_ids
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Register a new user connection."""
        self.connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total: {len(self.connections)}")

    async def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)
        for users in self.rooms.values():
            users.discard(user_id)
        logger.info(f"User {user_id} disconnected. Total: {len(self.connections)}")

    async def connect_room(self, user_id: str, room_id: str):
        """Add user to a room."""
        if user_id not in self.connections:
            raise ValueError(f"User {user_id} not connected")
        self.rooms.setdefault(room_id, set()).add(user_id)
        logger.info(f"User {user_id} joined room {room_id}")

    async def disconnect_room(self, user_id: str, room_id: str):
        """Remove user from a room."""
        if room_id in self.rooms:
            self.rooms[room_id].discard(user_id)
        logger.info(f"User {user_id} left room {room_id}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to a single user."""
        ws = self.connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast(self, user_ids: Set[str], message: dict):
        """Send a message to a set of users."""
        for uid in user_ids:
            await self.send_to_user(uid, message)

    async def broadcast_room(self, room_id: str, message: dict):
        """Broadcast message to all users in a room."""
        user_ids = self.rooms.get(room_id, set())
        await self.broadcast(user_ids, message)

    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected users."""
        await self.broadcast(set(self.connections.keys()), message)

connection_manager = ConnectionManager()
