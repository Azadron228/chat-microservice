from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from pydantic import ValidationError
from app.api.deps.auth import get_current_user
from app.core.rpc import dispatch
from app.models.rpc import RPCRequest
import app.api.ws.handlers

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                raw_data = await websocket.receive_json()
                request = RPCRequest(**raw_data)
            except ValidationError as e:
                await websocket.send_json({
                    "error": {"code": -32600, "message": f"Invalid Request: {e.errors()}"},
                    "id": raw_data.get("id") if isinstance(raw_data, dict) else None
                })
                continue

            response = await dispatch(websocket, request)
            if response:
                await websocket.send_json(response.model_dump(exclude_none=True))

    except WebSocketDisconnect:
        pass
