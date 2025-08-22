import logging
from fastapi import FastAPI
from app.router import router
import app.logging
from app.config import settings

logger = logging.getLogger(__name__)

logger.info("App Started")
app = FastAPI()

url = settings.POSTGRES_DB_URL
logger.info(f"Connecting to Db with url: {url}")

app.include_router(router=router)