from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.core.messaging.factory import broker
from app.api.jsonrpc import router
import app.core.logging
from app.core.messaging.handlers import subscribe_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await broker.connect()
        await subscribe_handlers()
        logger.info("Connected to broker")
        yield
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received, shutting down...")
    except Exception as e:
        logger.exception("Error during lifespan setup")
        raise
    finally:
        await broker.close()
        logger.info("Broker closed")


app = FastAPI(lifespan=lifespan)
logger.info("Statred")

app.include_router(router)


@app.get("/health")
async def health():
    return "ok"
