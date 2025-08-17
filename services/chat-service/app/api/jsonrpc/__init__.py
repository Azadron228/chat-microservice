from fastapi import WebSocket, APIRouter, status
from app.core.auth.service import verify_token
import logging
from app.api.jsonrpc.handlers.chat import jsonrpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

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
    
    websocket.scope["token"] = token
    
    claims = await verify_token(token)
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
                resp = await jsonrpc.handle_jsonrpc_request(req_data, websocket, user_id = claims.sub)
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
            resp = await jsonrpc.handle_jsonrpc_request(data, websocket, user_id=claims.sub)
            if resp and resp.id is not None:  # Not a notification
                await websocket.send_json(resp.model_dump(exclude_unset=True))
