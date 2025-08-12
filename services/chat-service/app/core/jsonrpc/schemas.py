import asyncio
from typing import Any, Optional, Union
from fastapi import FastAPI, WebSocket, APIRouter
from pydantic import BaseModel, ValidationError
from inspect import signature


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Union[list, dict]] = None
    id: Optional[Union[str, int]] = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None
    id: Optional[Union[str, int]] = None