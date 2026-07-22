#!/bin/sh

set -eu

api_port=8000
uvicorn_pattern="uvicorn[[:space:]]+app\.main:app.*--port[[:space:]]+$api_port"
api_pids=$(pgrep -f "$uvicorn_pattern" 2>/dev/null || true)

if [ -z "$api_pids" ]; then
  printf 'Development API is not running.\n'
  exit 0
fi

printf 'Stopping development API process(es): %s\n' "$api_pids"
kill -TERM $api_pids 2>/dev/null || true

attempt=0
remaining="$api_pids"
while [ "$attempt" -lt 10 ] && [ -n "$remaining" ]; do
  next_remaining=""
  for pid in $remaining; do
    if kill -0 "$pid" 2>/dev/null; then
      next_remaining="$next_remaining $pid"
    fi
  done
  remaining=$(printf '%s' "$next_remaining" | sed 's/^ *//')
  [ -z "$remaining" ] || sleep 1
  attempt=$((attempt + 1))
done

if [ -n "$remaining" ]; then
  printf 'Development API did not stop gracefully; forcing shutdown.\n' >&2
  kill -KILL $remaining 2>/dev/null || true
fi

printf 'Development API stopped.\n'
