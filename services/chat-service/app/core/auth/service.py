
import logging
import jwt
from jwt import PyJWKClient
from typing import Optional
from app.core.auth.schemas import TokenPayload

logger = logging.getLogger(__name__)

KEYCLOAK_DOMAIN = "http://keycloack.local:8080"
REALM = "chat"
CLIENT_ID = "chat"
JWKS_URL = f"{KEYCLOAK_DOMAIN}/realms/{REALM}/protocol/openid-connect/certs"
TOKEN_URL = f"{KEYCLOAK_DOMAIN}/realms/{REALM}/protocol/openid-connect/token"

jwks_client = PyJWKClient(JWKS_URL)

async def verify_token(token: str) -> Optional[TokenPayload]:
    """Verify JWT token and return validated payload."""
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        issuer=f"{KEYCLOAK_DOMAIN}/realms/{REALM}",
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
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
    