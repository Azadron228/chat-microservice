
import logging
import jwt
from jwt import PyJWKClient
from typing import Optional
from app.core.auth.schemas import TokenPayload
from app.core.config import KeycloakSettings

logger = logging.getLogger(__name__)

jwks_client = PyJWKClient(KeycloakSettings.jwks_url)

async def verify_token(token: str) -> Optional[TokenPayload]:
    """Verify JWT token and return validated payload."""
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        issuer=f"{KeycloakSettings.KEYCLOAK__DOMAIN}/realms/{KeycloakSettings.KEYCLOAK_REALM}",
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=KeycloakSettings.KEYCLOAK_CLIENT_ID,
            issuer=issuer,
            options={
                "verify_aud": False,
                "verify_exp": False,
                "verify_iss": False,
            }
        )
        
        return TokenPayload(**payload)
    except jwt.InvalidTokenError as e:
        logger.error(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None
    