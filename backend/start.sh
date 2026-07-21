#!/usr/bin/env bash

set -Eeuo pipefail

backend_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
run_dir="$backend_dir/.run"
pid_file="$run_dir/uvicorn.pid"
log_file="$run_dir/uvicorn.log"
api_health_url="http://127.0.0.1:8000/v1/health"

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required. Install uv before running this script.\n' >&2
  exit 1
fi

mkdir -p "$run_dir"
if [[ -f "$pid_file" ]]; then
  pid="$(<"$pid_file")"
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    printf 'Development API is already running (PID %s).\n' "$pid"
    exit 0
  fi
  if [[ "$pid" =~ ^[0-9]+$ ]] && [[ -d "/proc/$pid" ]]; then
    printf 'Cannot manage the existing development API (PID %s).\n' "$pid" >&2
    exit 1
  fi
  rm -f "$pid_file"
fi

cd "$backend_dir"
uv run alembic upgrade head

setsid uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir "$backend_dir/app" \
  >"$log_file" 2>&1 &
pid=$!
printf '%s\n' "$pid" >"$pid_file"

printf 'Starting development API (PID %s).\n' "$pid"
printf 'API:  http://127.0.0.1:8000/v1/health\n'
printf 'Docs: http://127.0.0.1:8000/docs\n\n'

if command -v curl >/dev/null 2>&1; then
  for _ in {1..10}; do
    if health_response="$(curl --fail --silent "$api_health_url" 2>/dev/null)"; then
      printf '%s\n' "$health_response"
      exit 0
    fi
    sleep 1
  done
  kill -- "-$pid" 2>/dev/null || true
  rm -f "$pid_file"
  printf 'API did not become healthy within 10 seconds. Check logs at:\n' >&2
  printf '%s\n' "$log_file" >&2
  exit 1
fi
