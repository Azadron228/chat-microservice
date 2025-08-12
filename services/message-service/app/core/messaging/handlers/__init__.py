from .message import handle_new_message
from app.core.messaging.factory import broker

broker.subscribe("*message.new",handle_new_message)
