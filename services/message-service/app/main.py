import json
import uuid
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.connection import setup
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine import connection
from app.protos import message_pb2, message_pb2_grpc
from app.server import serve

from app.nats import connect_nats, disconnect_nats, nc, nats_message_handler
from app.repo import MessageRepository

async def main():
    global repo
    repo = MessageRepository()

    await connect_nats()
    await nc.subscribe("message.created", cb=nats_message_handler)

    print("NATS connected and message handler set up.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        repo.close()
        await disconnect_nats()

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())