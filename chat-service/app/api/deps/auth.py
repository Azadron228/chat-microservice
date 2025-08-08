from fastapi import WebSocket, WebSocketException, status

async def get_current_user(websocket: WebSocket):
    auth = websocket.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing or invalid Authorization header"
        )

    token = auth[len("Bearer "):]
    return True