
from common.messaging.nats import NATSBroker

def get_broker() -> NATSBroker:
    return NATSBroker("nats://nats:4222")

broker = get_broker()