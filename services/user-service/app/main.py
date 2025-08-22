from fastapi import FastAPI
from app.router import router
from app.logging import logging
import logging
from app.config import settings

logger = logging.getLogger(__name__)

app = FastAPI()

logger.info("Starting User Service...")
logger.info(f"Database URL: {settings.jwks_url}")
logger.info(f"Database URL: {settings.issuer}")



app.include_router(router=router)