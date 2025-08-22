import uuid
from typing import List, Optional

from sqlalchemy import select

from app.database import Database
from app.models import User


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    async def create_user(
        self, id: uuid.UUID, email: str, preferred_username: str | None = None
    ) -> User:
        async with self.db.get_session() as session:
            user = User(id=id, email=email, preferred_username=preferred_username)
            session.add(user)
            await session.flush()
            return user

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        async with self.db.get_session() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_users(self) -> List[User]:
        async with self.db.get_session() as session:
            stmt = select(User)
            result = await session.execute(stmt)
            return result.scalars().all()

