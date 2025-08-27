from app.messaging.handlers.message import handle_message_update
from app.messaging.factory import broker


async def subscribe_handlers():
    await broker.subscribe("chat.room.update_last_message", handle_message_update)
