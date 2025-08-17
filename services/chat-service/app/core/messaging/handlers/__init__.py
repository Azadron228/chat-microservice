from app.core.messaging.factory import broker
from app.core.messaging.handlers.chat import to_broadcast_handler

async def subscribe_handlers():
    await broker.subscribe("chat.messages.to_broadcast", to_broadcast_handler)