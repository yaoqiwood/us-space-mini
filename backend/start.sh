#!/bin/sh

set -eu

backend_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
pid_file="$backend_dir/.run/uvicorn.pid"
api_port=8000
uvicorn_pattern="uvicorn[[:space:]]+app\.main:app.*--port[[:space:]]+$api_port"

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required. Install uv before running this script.\n' >&2
  exit 1
fi

list_api_pids() {
  pgrep -f "$uvicorn_pattern" 2>/dev/null || true
}

port_is_in_use() {
  if command -v fuser >/dev/null 2>&1; then
    fuser -s -n tcp "$api_port"
    return
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$api_port" -sTCP:LISTEN >/dev/null 2>&1
    return
  fi
  return 1
}

stop_running_api() {
  api_pids=$(list_api_pids)
  if [ -n "$api_pids" ]; then
    printf 'Stopping existing development API process(es): %s\n' "$api_pids"
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
      printf 'Force stopping development API process(es): %s\n' "$remaining" >&2
      kill -KILL $remaining 2>/dev/null || true
    fi
  fi

  rm -f "$pid_file"
  if port_is_in_use; then
    printf 'Port %s is still occupied by a process that is not this development API.\n' "$api_port" >&2
    printf 'Refusing to terminate an unknown process. Stop it manually, then run this script again.\n' >&2
    exit 1
  fi
}

stop_running_api

cd "$backend_dir"
uv run alembic upgrade head

printf 'Starting development API in the foreground.\n'
printf 'API:  http://127.0.0.1:%s/v1/health\n' "$api_port"
printf 'Docs: http://127.0.0.1:%s/docs\n\n' "$api_port"

exec uv run uvicorn app.main:app --host 127.0.0.1 --port "$api_port" --reload --reload-dir "$backend_dir/app"
