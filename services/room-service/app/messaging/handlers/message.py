from datetime import datetime
import logging
import uuid
from app.deps import repo

logger = logging.getLogger(__name__)


async def handle_message_update(data: dict):
    try:
        room_id = uuid.UUID(data["room_id"])
        message_id = data["message_id"]
        author_id = data["author_id"]
        content = data["content"]
        created_at = datetime.fromisoformat(data["created_at"])

        await repo.update_last_message(
            room_id=room_id,
            message_id=message_id,
            preview=content,
            created_at=created_at,
            author_id=author_id,
        )

        logger.info(f"Updated last message for room {room_id} -> {data}")

    except Exception as e:
        logger.error(f"Error updating last message for room {data.get('room_id')}: {e}")