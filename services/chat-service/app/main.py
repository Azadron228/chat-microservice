from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.core.messaging.factory import broker
from app.api.jsonrpc import router
import app.core.logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    logger.info("Conneced to broker")
    try:
        yield
    finally:
        await broker.close()

app = FastAPI(lifespan=lifespan)
logger.info("Statred")

app.include_router(router)


@app.get("/health")
async def health():
    return "ok"