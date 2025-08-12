
from app.core.messaging.nats import NATSBroker
from app.core.config import settings

def get_broker() -> NATSBroker:
    return NATSBroker(settings.NATS_URL)

broker = get_broker()