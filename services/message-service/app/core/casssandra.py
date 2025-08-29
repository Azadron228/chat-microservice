import asyncio
from contextlib import asynccontextmanager
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from app.core.config import settings

cluster = Cluster(
    contact_points=[settings.SCYLLADB_URL],
    compression=True,
    load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
)


session = cluster.connect("chat")

