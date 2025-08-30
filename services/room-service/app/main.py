from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.router import router
import app.logging
from app.config import settings
from app.messaging.factory import broker
from app.messaging.handlers import subscribe_handlers

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



app = FastAPI(
    lifespan=lifespan,
    servers=[
        {"url": "https://localhost:8010/", "description": "Development server"},
    ],
)

url = settings.POSTGRES_DB_URL
logger.info(f"Connecting to Db with url: {url}")

app.include_router(router=router)