from enum import Enum
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    LOCAL = "local"
    
class BaseAppSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEV

class KeycloackSettings(BaseAppSettings):
    DOMAIN: str
    REALM: str
    CLIENT_ID: str

    @property
    def jwks_url(self) -> str:
        return f"{self.DOMAIN}/realms/{self.REALM}/protocol/openid-connect/certs"

    @property
    def token_url(self) -> str:
        return f"{self.DOMAIN}/realms/{self.REALM}/protocol/openid-connect/token"

    @property
    def issuer(self) -> str:
        return f"{self.DOMAIN}/realms/{self.REALM}"
    
class Settings(KeycloackSettings, BaseAppSettings):
    NATS_URL: str
    MESSAGE_SERVICE_GRPC_URL: str
    class Config:
        env_file = ("../../.env")
        extra = "ignore"

settings = Settings()