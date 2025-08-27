import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.base import Base


class Room(Base):
    __tablename__ = "rooms"

    room_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    type: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=255), nullable=True)
    alias: Mapped[str] = mapped_column(sa.String(length=255), nullable=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)

    last_message_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, nullable=True)
    last_message_preview: Mapped[str] = mapped_column(sa.String(length=255), nullable=True)
    last_message_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    last_message_sender_id: Mapped[str] = mapped_column(sa.String(length=64), nullable=True)

    members: Mapped[list["RoomMember"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class RoomMember(Base):
    __tablename__ = "room_members"

    room_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("rooms.room_id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        sa.String(length=64), primary_key=True
    )

    unread_count: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    room: Mapped["Room"] = relationship(back_populates="members")
