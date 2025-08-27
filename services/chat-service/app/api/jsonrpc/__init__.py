from fastapi import WebSocket, APIRouter, status
from app.core.auth.service import verify_token
import logging
from app.core.jsonrpc.dispatcher import JsonRpcRouter
from app.api.jsonrpc.handlers.chat import jsonrpc as chat_router
from app.core.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()
jsonrpc_router = JsonRpcRouter()
jsonrpc_router.include_router(chat_router)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    token = websocket.query_params.get("token")

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
    user_id = claims.sub
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                break

            await connection_manager.disconnect(user_id)
            
            if isinstance(data, list):
                # Batch request
                responses = []
                for req_data in data:
                    resp = await jsonrpc_router.dispatch(req_data, websocket, user_id = claims.sub)
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
                resp = await jsonrpc_router.dispatch(data, websocket, user_id=claims.sub)
                if resp and resp.id is not None:  # Not a notification
                    await websocket.send_json(resp.model_dump(exclude_unset=True))

    finally:
        await connection_manager.disconnect(user_id)
