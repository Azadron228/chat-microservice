from app.database import Database
from app.config import settings
from app.repo import RoomRepository

db = Database(
    url=settings.DATABASE_URL,
)

async def get_db():
    return db

async def get_repo() -> RoomRepository:
    return RoomRepository(db)