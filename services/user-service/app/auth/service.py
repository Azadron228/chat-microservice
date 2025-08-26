
import logging
import jwt
from jwt import PyJWKClient
from typing import Optional
from app.auth.schemas import TokenPayload
from app.config import KeycloakSettings, settings

logger = logging.getLogger(__name__)

jwks_client = PyJWKClient(settings.jwks_url)


async def verify_token(token: str) -> Optional[TokenPayload]:
    """Verify JWT token and return validated payload."""
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        logger.info(f"Verifying token with issuer: {settings.issuer}")
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.issuer,
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
    