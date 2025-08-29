import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union
from app.repo import RoomRepository
from app.deps import get_current_user, provide_room_service, provide_room_repo
from app.schemas import RoomCreate, RoomMemberOut, RoomOut, DmRoomOut
from app.auth.schemas import TokenPayload
from app.service import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[Union[RoomOut, DmRoomOut]])
async def list_rooms(
    user: TokenPayload = Depends(get_current_user),
    service: RoomService = Depends(provide_room_service),
):
    return await service.list_rooms(user_id=user.sub)


@router.get("/{room_id}", response_model=Union[RoomOut, DmRoomOut])
async def get_room(
    room_id: uuid.UUID,
    user: TokenPayload = Depends(get_current_user),
    service: RoomService = Depends(provide_room_service),
):
    room = await service.get_room(room_id=room_id, user_id=user.sub)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    return room

@router.get("/dm/{user_id}", response_model=Union[RoomOut, DmRoomOut])
async def get_dm_room(
    user_id: uuid.UUID,
    user: TokenPayload = Depends(get_current_user),
    service: RoomService = Depends(provide_room_service),
):
    room = await service.get_dm(user_id1=user_id, user_id2=user.sub)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    return room


@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    user: TokenPayload = Depends(get_current_user),
    service: RoomService = Depends(provide_room_service),
):
    data.members.append(user.sub)
    room = await service.create_room(data)
    return room


@router.post(
    "/dm/{user_id}", response_model=DmRoomOut, status_code=status.HTTP_201_CREATED
)
async def create_dm_room(
    user_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: RoomService = Depends(provide_room_service),
):
    if user_id == current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot get DM with yourself",
        )
    
    room = await service.start_dm(current_user.sub, user_id)
    return room


@router.get("/{room_id}/members", response_model=List[RoomMemberOut])
async def list_room_members(
    room_id: uuid.UUID,
    user: TokenPayload = Depends(get_current_user),
    repo: RoomRepository = Depends(provide_room_repo),
):
    members = await repo.list_members(room_id=room_id)
    return members

