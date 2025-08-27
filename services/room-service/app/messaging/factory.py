
from app.messaging.nats import NATSBroker
from app.config import settings

def get_broker() -> NATSBroker:
    return NATSBroker(settings.NATS_URL)

broker = get_broker()