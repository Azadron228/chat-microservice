import asyncio
from typing import Any, Optional, Union
from fastapi import FastAPI, WebSocket, APIRouter
from pydantic import BaseModel, ValidationError
from inspect import signature
import app.api.jsonrpc.handlers
from app.core.jsonrpc.dispatcher import handle_jsonrpc_request

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = {
        "name": "Azadron"
    }
    while True:
        try:
            data = await websocket.receive_json()
        except Exception:
            break  # Connection closed or error

        if isinstance(data, list):
            # Batch request
            responses = []
            for req_data in data:
                resp = await handle_jsonrpc_request(req_data, websocket, user)
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
            resp = await handle_jsonrpc_request(data, websocket, user)
            if resp and resp.id is not None:  # Not a notification
                await websocket.send_json(resp.model_dump(exclude_unset=True))
