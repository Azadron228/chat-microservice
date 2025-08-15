from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NATS_URL: str
    MESSAGE_SERVICE_GRPC_URL: str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()