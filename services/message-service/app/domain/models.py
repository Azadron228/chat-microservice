from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
import uuid
from datetime import datetime


class MessageStatus:
    DELIVERED = 0
    SEEN = 1


class Message(Model):
    __keyspace__ = "chat"
    room_id = columns.Text(partition_key=True)
    created_at = columns.DateTime(primary_key=True)
    updated_at = columns.DateTime(primary_key=True)
    message_id = columns.UUID(default=uuid.uuid4)
    sender_id = columns.Text()
    content = columns.Text()
    media_ids = columns.List(columns.UUID)
    reply_to = columns.UUID(required=False)
    quote = columns.Text(required=False)


class MessageUserStatus(Model):
    __keyspace__ = "chat"

    message_id = columns.UUID(primary_key=True, partition_key=True)
    user_id = columns.Text(primary_key=True)
    status = columns.Integer()
    delivered_at = columns.DateTime()
    seen_at = columns.DateTime()
