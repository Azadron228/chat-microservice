import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(), unique=True)
    preferred_username: Mapped[str] = mapped_column(sa.String())
