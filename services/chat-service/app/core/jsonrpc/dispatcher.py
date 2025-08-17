import asyncio
import logging
from typing import Callable, Optional
from fastapi import WebSocket
from pydantic import ValidationError
from inspect import signature
from app.core.jsonrpc.schemas import JsonRpcRequest, JsonRpcResponse, JsonRpcError

logger = logging.getLogger(__name__)

class JsonRpcRouter:
    def __init__(self):
        self.methods: dict[str, Callable] = {}
        
    def method(self, name: Optional[str] = None):
        """
        Decorator to register a function as a JSON-RPC method.

        Usage:
        @jsonrpc_method()
        async def my_method(param1: int, param2: str) -> str:
            return f"Result: {param1} {param2}"

        Or with custom name:
        @jsonrpc_method("custom.method")
        async def my_method(...):
            ...
        """

        def decorator(func):
            method_name = name or func.__name__
            self.methods[method_name] = func
            return func

        return decorator


    async def handle_jsonrpc_request(
        self, req_data: dict, websocket: WebSocket, user_id: str
    ) -> Optional[JsonRpcResponse]:
        try:
            request = JsonRpcRequest(**req_data)
        except ValidationError:
            return JsonRpcResponse(
                id=None, error=JsonRpcError(code=-32700, message="Parse error")
            )

        if request.jsonrpc != "2.0":
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=-32600, message="Invalid Request - Unsupported version"
                ),
            )

        if request.method not in self.methods:
            return JsonRpcResponse(
                id=request.id, error=JsonRpcError(code=-32601, message="Method not found")
            )

        func = self.methods[request.method]

        try:
            if isinstance(request.params, list):
                args = request.params
                kwargs = {}
            elif isinstance(request.params, dict):
                args = []
                kwargs = request.params
            else:
                args = []
                kwargs = {}

            sig = signature(func)

            # Inject context parameters if the function accepts them (override if provided)
            extra_kwargs = {"websocket": websocket, "user_id": user_id}
            for extra_name, extra_value in extra_kwargs.items():
                if extra_name in sig.parameters:
                    kwargs[extra_name] = extra_value

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            return JsonRpcResponse(id=request.id, result=result)
        except TypeError as e:
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32602, message=f"Invalid params: {str(e)}"),
            )
        except Exception as e:
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32603, message=f"Internal error: {str(e)}"),
            )
