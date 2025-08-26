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
    await connection_manager.broadcast(user_ids=["1ec4bb14-9b95-44a5-b608-e5efbd9a31b4", "b0ab9326-a1f1-4363-b501-a136baaf2376"], message=json.dumps(msg))
    