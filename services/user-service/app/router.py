import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.service import UserService
from app.deps import get_user_service, get_current_user
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.list_users()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: uuid.UUID, 
    service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.get("/me/", response_model=UserOut)
async def get_current_user(
    user: User = Depends(get_current_user)
):
    return user