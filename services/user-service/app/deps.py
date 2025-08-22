from app.database import Database
from app.config import settings
from app.repo import UserRepository
from app.service import UserService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.auth.service import verify_token
from app.auth.schemas import TokenPayload


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="http://localhost:8080/realms/chat/protocol/openid-connect/auth",
    tokenUrl="http://localhost:8080/realms/chat/protocol/openid-connect/token"
)

db = Database(
    url=settings.POSTGRES_DB_URL,
)


async def get_db():
    return db


async def get_user_repo(db: Database = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_user_service(
    repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
):
    payload: TokenPayload | None = await verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_user(user_id=payload.sub)

    if not user:
        # Create user if not exists
        user = await user_service.create_user(
            id=payload.sub,
            email=payload.email,
            preferred_username=payload.preferred_username or None,
        )

    return user
