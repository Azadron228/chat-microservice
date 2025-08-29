docker exec -it chat-server-user-service-1 alembic upgrade head
docker exec -it chat-server-room-service-1 alembic upgrade head
docker exec -i chat-server-scylla-1 cqlsh < shared/cassandra/message-schema.cql