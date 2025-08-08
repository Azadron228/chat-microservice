

from app.core.config.nats import NatsSettings


class Settings(
    NatsSettings,
):
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()