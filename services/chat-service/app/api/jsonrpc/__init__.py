import asyncio
from typing import Any, Optional, Dict, Union
from fastapi import FastAPI, WebSocket, APIRouter, status
from pydantic import BaseModel
import jwt
from jwt import PyJWKClient, PyJWKClientError
from datetime import datetime, timedelta
import aiohttp
import logging
from app.core.jsonrpc.dispatcher import handle_jsonrpc_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Keycloak configuration
KEYCLOAK_DOMAIN = "http://keycloack.local:8080"
REALM = "chat"
CLIENT_ID = "chat"
JWKS_URL = f"{KEYCLOAK_DOMAIN}/realms/{REALM}/protocol/openid-connect/certs"
TOKEN_URL = f"{KEYCLOAK_DOMAIN}/realms/{REALM}/protocol/openid-connect/token"

# Cache for JWKS
_jwks_client: Optional[PyJWKClient] = None
_jwks_last_updated: Optional[datetime] = None
_jwks_cache_duration = timedelta(minutes=60)

async def fetch_jwks() -> Dict:
    """Fetch JWKS data asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(JWKS_URL) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to fetch JWKS: HTTP {response.status}")
                raise PyJWKClientError(f"Failed to fetch JWKS: HTTP {response.status}")
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e}")
        raise PyJWKClientError(f"Error fetching JWKS: {e}")
    
async def get_jwks_client() -> PyJWKClient:
    """Get or refresh JWKS client with caching."""
    global _jwks_client, _jwks_data, _jwks_last_updated
    
    current_time = datetime.utcnow()
    
    if (_jwks_client is None or 
        _jwks_last_updated is None or 
        current_time - _jwks_last_updated > _jwks_cache_duration):
        try:
            _jwks_data = await fetch_jwks()
            _jwks_client = PyJWKClient(JWKS_URL)
            _jwks_last_updated = current_time
            logger.info("JWKS client refreshed successfully")
        except PyJWKClientError as e:
            logger.error(f"Failed to initialize JWKS client: {e}")
            raise
    return _jwks_client

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    exp: int
    iat: int
    aud: Union[str, list]

async def verify_token(token: str) -> Optional[TokenPayload]:
    """Verify JWT token and return validated payload."""
    try:
        jwks_client = await get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        issuer=f"{KEYCLOAK_DOMAIN}/realms/{REALM}",
        logger.info(f"Issuer: {issuer}")
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer="http://localhost:8080/realms/chat",
            options={
                "verify_signature": True,
                "verify_aud": False,
                "verify_iat": True,
                "verify_exp": True,
                "verify_iss": True,
            }
        )
        logger.info(f"Payload: {payload}")
        
        return TokenPayload(**payload)
    except jwt.InvalidTokenError as e:
        logger.error(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None

async def refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh access token using refresh token."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TOKEN_URL,
                data={
                    "client_id": CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Token refresh failed with status {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint with Keycloak authentication."""
    await websocket.accept()
    
   # 1. Check query param
    token = websocket.query_params.get("token")

    # 2. If not found, check Authorization header
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    claims = verify_token(token)
    if not claims:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Store user info in WebSocket scope
    websocket.scope["user"] = claims
    
    while True:
        try:
            data = await websocket.receive_json()
        except Exception:
            break  # Connection closed or error

        if isinstance(data, list):
            # Batch request
            responses = []
            for req_data in data:
                resp = await handle_jsonrpc_request(req_data, websocket, user_id = claims["sub"])
                if (
                    resp and resp.id is not None
                ):  # Only include responses for requests with id (not notifications)
                    responses.append(resp)
            if responses:
                await websocket.send_json(
                    [r.model_dump(exclude_unset=True) for r in responses]
                )
        else:
            # Single request
            resp = await handle_jsonrpc_request(data, websocket, user_id=claims["sub"])
            if resp and resp.id is not None:  # Not a notification
                await websocket.send_json(resp.model_dump(exclude_unset=True))
