import json
import logging
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator

logger = logging.getLogger(__name__)
class PostgresSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB_URL: str | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_postgres_url(cls, values: dict[str, str]) -> dict[str, str]:
        if values.get("POSTGRES_DB_URL"):
            return values

        username = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST")
        port = values.get("POSTGRES_PORT")
        db_name = values.get("POSTGRES_DB")
        values["POSTGRES_DB_URL"] = (
            f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"
        )

        return values

    @property
    def test_postgres_db(self) -> str:
        return f"test_{self.POSTGRES_DB}"
    
    logger.info(f"Database url: {POSTGRES_DB_URL}")

    @property
    def test_postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.test_postgres_db}"
    
class KeycloakSettings(BaseSettings):
    KEYCLOAK_DOMAIN: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: List[str]

    @property
    def jwks_url(self) -> str:
        return f"{self.KEYCLOAK_DOMAIN}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    @property
    def token_url(self) -> str:
        return f"{self.KEYCLOAK_DOMAIN}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"

    @property
    def issuer(self) -> str:
        return f"{self.KEYCLOAK_DOMAIN}/realms/{self.KEYCLOAK_REALM}"

    @field_validator("KEYCLOAK_CLIENT_ID", mode="before")
    def parse_json_list(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
class Settings(PostgresSettings, KeycloakSettings):
    NATS_URL: str = "nats://nats:4222"
    class Config:
        env_prefix = "ROOM_"
        env_file = "../../.env"
        extra = "ignore"
        
settings = Settings()
