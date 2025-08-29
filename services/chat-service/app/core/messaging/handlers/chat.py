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
    
    await connection_manager.send_to_active_users(room_id=msg["room_id"], message=json.dumps(msg))
    