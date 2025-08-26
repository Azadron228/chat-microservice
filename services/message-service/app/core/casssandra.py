import asyncio
from contextlib import asynccontextmanager
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from app.core.config import settings

cluster = Cluster(
    contact_points=[settings.SCYLLADB_URL],
    compression = True
)


@asynccontextmanager
async def get_session():
    try:
        session = cluster.connect("chat")
        yield session
    finally:
        pass

async def await_response_future(future):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, future.result)
