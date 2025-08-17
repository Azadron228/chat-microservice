async def register_jsonrpc_methods():
    from app.api.jsonrpc.handlers.chat import jsonrpc as chat_router