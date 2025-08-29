from app.messaging.handlers.message import handle_message_update
from app.messaging.factory import broker


async def subscribe_handlers():
    await broker.subscribe("chat.room.update_list", handle_message_update)
 