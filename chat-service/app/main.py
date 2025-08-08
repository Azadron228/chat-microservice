from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.nats import connect_nats, disconnect_nats
from app.api.ws.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_nats()
    yield
    await disconnect_nats()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
