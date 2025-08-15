#!/usr/bin/env bash
python -m grpc_tools.protoc \
    -I../../shared \
    --python_out=. \
    --grpc_python_out=. \
    ../../shared/protos/message.proto

echo "✅ Protobufs generated for chat-service"
