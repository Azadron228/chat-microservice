import uuid
from typing import Optional, Sequence
from app.models import User
from app.repo import UserRepository
from app.auth.schemas import TokenPayload

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def list_users(self) -> Sequence[User]:
        return await self.repo.list_users()
    
    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.repo.get_user(user_id)

    async def create_user(self, id: uuid.UUID, email: str, preferred_username: str = None) -> User:
        return await self.repo.create_user(
            id=id,
            email=email,
            preferred_username=preferred_username
        )