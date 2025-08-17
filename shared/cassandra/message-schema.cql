CREATE KEYSPACE IF NOT EXISTS chat
WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};


CREATE TABLE IF NOT EXISTS chat.messages (
    room_id UUID,
    message_id UUID,
    author_id UUID,
    content TEXT,
    media_ids LIST<UUID>,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((room_id), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);


CREATE TABLE IF NOT EXISTS chat.message_user_status (
    message_id UUID,
    user_id UUID,
    delivered_at TIMESTAMP,
    seen_at TIMESTAMP,
    PRIMARY KEY ((message_id), user_id)
);