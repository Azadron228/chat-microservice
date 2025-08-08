
from pydantic_settings import BaseSettings

class NatsSettings(BaseSettings):
    NATS_URL: str = "nats://nats:4222"

