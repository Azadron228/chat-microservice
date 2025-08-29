CREATE KEYSPACE IF NOT EXISTS chat
WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};


CREATE TABLE chat.messages (
    room_id UUID,
    bucket INT,
    message_id UUID,
    author_id UUID,
    content TEXT,
    status TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY ((room_id, bucket), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);

CREATE TABLE chat.user_message_status (
    user_id UUID,
    room_id UUID,
    message_id UUID,
    delivered_at TIMESTAMP,
    seen_at TIMESTAMP,
    PRIMARY KEY ((user_id, room_id), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
