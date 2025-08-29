from app.database import Database
from app.config import settings
from app.repo import RoomRepository
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.auth.service import verify_token
from app.auth.schemas import TokenPayload
from fastapi import HTTPException, status
from app.service import RoomService

db = Database(
    url=settings.POSTGRES_DB_URL,
)

repo = RoomRepository(db)
service = RoomService(repo)

async def get_db():
    return db

async def provide_room_repo() -> RoomRepository:
    return repo

async def provide_room_service() -> RoomService:
    return service

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="http://localhost:8080/realms/chat/protocol/openid-connect/auth",
    tokenUrl="http://localhost:8080/realms/chat/protocol/openid-connect/token"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    payload: TokenPayload | None = await verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload