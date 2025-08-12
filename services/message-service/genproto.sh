#!/usr/bin/env bash
set -e

# Absolute path to repo root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PROTO_SRC="$ROOT_DIR/shared/protos"
GEN_DIR="$ROOT_DIR/services/message-service/app/core/grpc/gen"

# Clean and recreate output dir
rm -rf "$GEN_DIR"
mkdir -p "$GEN_DIR"

python -m grpc_tools.protoc \
    -I "$PROTO_SRC" \
    --python_out="$GEN_DIR" \
    --grpc_python_out="$GEN_DIR" \
    "$PROTO_SRC"/*.proto

echo "✅ Protobufs generated for message-service in $GEN_DIR"
