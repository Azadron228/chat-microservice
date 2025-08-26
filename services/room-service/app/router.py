import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import RoomOut, RoomMemberOut, RoomCreate, MemberAdd
from app.repo import RoomRepository
from app.deps import get_repo

router = APIRouter()

@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
async def create_room(payload: RoomCreate, repo: RoomRepository = Depends(get_repo)):
    room = await repo.create_room(
        type_=payload.type,
        name=payload.name,
        alias=payload.alias,
        description=payload.description,
    )
    return room

@router.post("/rooms/dm", response_model=RoomOut)
async def get_or_create_dm(
    user_id1: str,
    user_id2: str,
    repo: RoomRepository = Depends(get_repo),
):
    return await repo.get_or_create_dm(user_id1, user_id2)

@router.get("/rooms", response_model=List[RoomOut])
async def list_rooms(repo: RoomRepository = Depends(get_repo)):
    return await repo.list_rooms()


@router.get("/rooms/{room_id}", response_model=RoomOut)
async def get_room(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
    room = await repo.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
    room = await repo.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    await repo.delete_room(room_id)
    return None


# --- Members ---

@router.post("/rooms/{room_id}/members", response_model=RoomMemberOut)
async def add_member(
    room_id: uuid.UUID,
    payload: MemberAdd,
    repo: RoomRepository = Depends(get_repo),
):
    room = await repo.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    member = await repo.add_member(room_id, payload.user_id)
    return member


@router.delete("/rooms/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    room_id: uuid.UUID, user_id: str, repo: RoomRepository = Depends(get_repo)
):
    if not await repo.is_member(room_id, user_id):
        raise HTTPException(status_code=404, detail="Member not found in this room")
    await repo.remove_member(room_id, user_id)
    return None


@router.get("/rooms/{room_id}/members", response_model=List[RoomMemberOut])
async def list_members(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
    return await repo.list_members(room_id)
