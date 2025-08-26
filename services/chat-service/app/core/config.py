from enum import Enum
import json
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    LOCAL = "local"
    
class BaseAppSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEV

class KeycloakSettings(BaseAppSettings):
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
    
class Settings(KeycloakSettings, BaseAppSettings):
    NATS_URL: str
    MESSAGE_SERVICE_GRPC_URL: str
    class Config:
        env_file = ["../../.env"]
        extra = "ignore"

settings = Settings()