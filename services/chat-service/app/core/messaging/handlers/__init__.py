from app.core.messaging.factory import broker
from app.core.messaging.handlers.chat import to_broadcast_handler
from app.core.messaging.handlers.room import room_list_update

async def subscribe_handlers():
    await broker.subscribe("chat.messages.to_broadcast", to_broadcast_handler)
    await broker.subscribe("chat.rooms.update_room_list", room_list_update)