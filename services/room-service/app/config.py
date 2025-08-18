from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_DB_URL = "postgresql+asyncpg://user:password@localhost/dbname"

settings = Settings()
