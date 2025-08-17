import json
import logging
from app.domain.chat.service import rooms,remove_client_from_all_rooms
from app.core.connection_manager import connection_manager
from app.domain.chat.room_service import room_service
logger = logging.getLogger(__name__)

async def to_broadcast_handler(msg):
    logger.info(f"Got message:{msg}")
    if not msg["room_id"]:
        return
    
    users = room_service.get_room_members(room_id=msg["room_id"])
    connection_manager.broadcast(user_ids=users)
    