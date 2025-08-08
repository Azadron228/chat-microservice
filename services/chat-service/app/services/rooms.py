from typing import Dict, Set
from fastapi import WebSocket

rooms: Dict[str, Set[WebSocket]] = {}

def add_client_to_room(room_id: str, ws: WebSocket):
    rooms.setdefault(room_id, set()).add(ws)

def remove_client_from_all_rooms(ws: WebSocket):
    empty_rooms = []
    for room_id, clients in rooms.items():
        clients.discard(ws)
        if not clients:
            empty_rooms.append(room_id)
    for room_id in empty_rooms:
        del rooms[room_id]
