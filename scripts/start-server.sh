#!/usr/bin/env bash
set -euo pipefail

# Send output to server.log
nohup uv run uvicorn kubeshield.server:app > server.log 2>&1 &

for attempt in $(seq 1 30); do
  if curl --silent --fail http://localhost:8000/health > /dev/null; then
    echo "Server is up"
    exit 0
  fi
  sleep 1
done

echo "Server timed out"
exit 1
