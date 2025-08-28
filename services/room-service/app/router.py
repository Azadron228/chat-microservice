import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.repo import RoomRepository
from app.deps import get_current_user, get_repo
from app.schemas import RoomCreate, RoomOut, DmRoomOut
from app.auth.schemas import TokenPayload

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", response_model=List[RoomOut])
async def list_rooms(
    user: TokenPayload = Depends(get_current_user), repo: RoomRepository = Depends(get_repo)
):
    return await repo.list_rooms(user_id=user.sub)

@router.post("/", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    user: TokenPayload = Depends(get_current_user),
    repo: RoomRepository = Depends(get_repo),
):  
    data.members.append(user.sub)
    room = await repo.create_room(data)
    return room


@router.post("/dm/{user_id}", response_model=DmRoomOut, status_code=status.HTTP_201_CREATED)
async def create_dm_room(
    user_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    repo: RoomRepository = Depends(get_repo),
):  
    room = await repo.get_or_create_dm(current_user.sub, user_id)
    display_name = next((m for m in room.members if m.user_id != current_user.sub))
    room.user_id = display_name.user_id
    return room

# @router.get("/", response_model=List[Room])
# async def list_rooms(
#     user_id: Optional[str] = None,
#     repo: RoomRepository = Depends(),
# ):
#     return await repo.list_rooms(user_id=user_id)


# @router.post("/", response_model=Room)
# async def create_room(
#     data: RoomCreate,
#     repo: RoomRepository = Depends(),
# ):
#     return await repo.create_room(data)


# @router.get("/{room_id}", response_model=Room)
# async def get_room(
#     room_id: UUID,
#     repo: RoomRepository = Depends(),
# ):
#     room = await repo.get_room(room_id)
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     return room


# @router.post("/{room_id}/last-message")
# async def update_last_message(
#     room_id: UUID,
#     data: RoomUpdateLastMessage,
#     repo: RoomRepository = Depends(),
# ):
#     await repo.update_last_message(room_id, data)
#     return {"status": "updated"}


# @router.post("/members", response_model=RoomMember)
# async def add_member(
#     data: MemberAdd,
#     repo: RoomRepository = Depends(),
# ):
#     return await repo.add_member(data)


# @router.delete("/{room_id}/members/{user_id}")
# async def remove_member(
#     room_id: UUID,
#     user_id: str,
#     repo: RoomRepository = Depends(),
# ):
#     await repo.remove_member(room_id, user_id)
#     return {"status": "removed"}


# @router.get("/{room_id}/members", response_model=List[RoomMember])
# async def list_members(
#     room_id: UUID,
#     repo: RoomRepository = Depends(),
# ):
#     return await repo.list_members(room_id)

# @router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
# async def create_room(payload: RoomCreate, repo: RoomRepository = Depends(get_repo)):
#     room = await repo.create_room(
#         type_=payload.type,
#         name=payload.name,
#         alias=payload.alias,
#         description=payload.description,
#     )
#     return room

# @router.post("/rooms/dm/{user_id}", response_model=RoomOut)
# async def get_or_create_dm(
#     user_id: str,
#     user = Depends(get_current_user),
#     repo: RoomRepository = Depends(get_repo),
# ):
#     return await repo.get_or_create_dm(user.sub, user_id)

# @router.get("/rooms", response_model=List[RoomOut])
# async def list_rooms(repo: RoomRepository = Depends(get_repo), user = Depends(get_current_user)):
#     return await repo.list_rooms_by_user(user_id=user.sub)


# @router.get("/rooms/{room_id}", response_model=RoomOut)
# async def get_room(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
#     room = await repo.get_room(room_id)
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     return room


# @router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_room(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
#     room = await repo.get_room(room_id)
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     await repo.delete_room(room_id)
#     return None


# # --- Members ---

# @router.post("/rooms/{room_id}/members", response_model=RoomMemberOut)
# async def add_member(
#     room_id: uuid.UUID,
#     payload: MemberAdd,
#     repo: RoomRepository = Depends(get_repo),
# ):
#     room = await repo.get_room(room_id)
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     member = await repo.add_member(room_id, payload.user_id)
#     return member


# @router.delete("/rooms/{room_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_member(
#     room_id: uuid.UUID, user_id: str, repo: RoomRepository = Depends(get_repo)
# ):
#     if not await repo.is_member(room_id, user_id):
#         raise HTTPException(status_code=404, detail="Member not found in this room")
#     await repo.remove_member(room_id, user_id)
#     return None


# @router.get("/rooms/{room_id}/members", response_model=List[RoomMemberOut])
# async def list_members(room_id: uuid.UUID, repo: RoomRepository = Depends(get_repo)):
#     return await repo.list_members(room_id)
