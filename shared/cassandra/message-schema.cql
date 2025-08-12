CREATE KEYSPACE IF NOT EXISTS chat
WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};


CREATE TABLE IF NOT EXISTS chat.messages (
    room_id TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    message_id UUID,
    sender_id TEXT,
    content TEXT,
    media_ids LIST<UUID>,
    reply_to UUID,
    quote TEXT,
    PRIMARY KEY ((room_id), message_id)
);


CREATE TABLE IF NOT EXISTS chat.message_user_status (
    message_id UUID,
    user_id TEXT,
    status INT, -- 0: delivered, 1: seen
    delivered_at TIMESTAMP,
    seen_at TIMESTAMP,
    PRIMARY KEY ((message_id), user_id)
);