import asyncio
from fastapi import WebSocket
import json
from nats.aio.client import Client as NATS
from app.core.config import settings
nc = NATS()

async def connect_nats():
    try:
        await asyncio.wait_for(
            nc.connect("nats://localhost:4222"),
            timeout=5
        )
        print("Connected to NATS!")
        return nc
    except asyncio.TimeoutError:
        print("❌ NATS connection timed out")
    except asyncio.CancelledError:
        print("❌ NATS connection task was cancelled")
        raise
    except Exception as e:
        print(f"❌ NATS connection failed: {e}")

async def disconnect_nats():
    await nc.close()
    await nc.drain()

async def publish_to_room(room_id: str, message: dict):
    await nc.publish(f"room.{room_id}", json.dumps(message).encode())


async def create_nats_message_handler(websocket: WebSocket):
    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())

            await websocket.send_json({
                "jsonrpc": "2.0",
                "method": data.get("type", "message"),
                "params": data
            })
        except Exception as e:
            print(f"NATS error: {e}")
    return handler
