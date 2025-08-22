import uuid
from pydantic import BaseModel


class UserCreate(BaseModel):
    id: uuid.UUID
    email: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str

    class Config:
        from_attributes = True
