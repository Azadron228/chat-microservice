import json
from nats.aio.client import Client as NATS
nc = NATS()

async def connect_nats():
    await nc.connect("nats://localhost:4222")

async def disconnect_nats():
    await nc.close()