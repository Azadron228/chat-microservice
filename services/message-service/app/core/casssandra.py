from contextlib import asynccontextmanager
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])

@asynccontextmanager
async def get_session():
    try:
        session = cluster.connect("chat")
        yield session
    finally:
        session.shutdown()
