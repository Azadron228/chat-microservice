from typing import Generic, TypeVar
from pydantic import BaseModel

class RPCRequest(BaseModel):
    method: str
    params: dict
    id: str | None = None

class RPCResponse(BaseModel):
    result: dict | None = None
    error: dict | None = None
    id: str | None = None
