from typing import Callable, Awaitable, Any, Dict

from pydantic import ValidationError
from app.models.rpc import RPCRequest, RPCResponse

rpc_registry: Dict[str, Callable[[Any, RPCRequest], Awaitable[RPCResponse]]] = {}

def rpc_method(name: str):
    def decorator(func: Callable[[Any, RPCRequest], Awaitable[RPCResponse]]):
        rpc_registry[name] = func
        return func
    return decorator

async def dispatch(websocket, request: RPCRequest) -> RPCResponse:
    handler = rpc_registry.get(request.method)
    if not handler:
        return RPCResponse(
            error={"code": -32601, "message": "Method not found"},
            id=request.id,
        )

    try:
        return await handler(websocket, request)

    except ValidationError as e:
        # This will catch any validation in handler like Pydantic(**params)
        return RPCResponse(
            error={"code": -32602, "message": "Invalid params", "details": e.errors()},
            id=request.id,
        )
    
    except Exception as e:
        return RPCResponse(
            error={"code": -32000, "message": f"Internal error: {str(e)}"},
            id=request.id,
        )
