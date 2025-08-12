CQL_FILE=shared/cassandra/message-schema.cql
CASSANDRA_CONTAINER=cassandra
PROTO_DIR = shared/protos
PROTO_FILE = $(PROTO_DIR)/message.proto

CHAT_PROTO_OUT = services/chat-service/app/protos
MESSAGE_PROTO_OUT = services/message-service/app/protos

create-schema:
	cat $(CQL_FILE) | docker exec -i $(CASSANDRA_CONTAINER) cqlsh




compile-protos:
	python -m grpc_tools.protoc -I$(PROTO_DIR) --python_out=$(CHAT_PROTO_OUT) --grpc_python_out=$(CHAT_PROTO_OUT) $(PROTO_FILE)
	python -m grpc_tools.protoc -I$(PROTO_DIR) --python_out=$(MESSAGE_PROTO_OUT) --grpc_python_out=$(MESSAGE_PROTO_OUT) $(PROTO_FILE)


init-db: create-schema
