#!/bin/sh

set -e

API1_URL="http://host.docker.internal:8020/openapi.json"
API2_URL="http://host.docker.internal:8010/openapi.json"

OUTPUT_DIR="$(cd "$(dirname "$0")/../docs/openapi" && pwd)"
OUTPUT_FILE="$OUTPUT_DIR/openapi.json"

mkdir -p "$OUTPUT_DIR"

echo "Running redocly join to combine remote API specifications..."

docker run --rm \
  -v "$OUTPUT_DIR":/out \
  redocly/cli join "$API1_URL" "$API2_URL" -o /out/openapi.json

echo "Combined API specification successfully created at $OUTPUT_FILE"
