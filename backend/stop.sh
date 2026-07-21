#!/usr/bin/env bash

set -Eeuo pipefail

backend_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
run_dir="$backend_dir/.run"
pid_file="$run_dir/uvicorn.pid"

if [[ ! -f "$pid_file" ]]; then
  printf 'Development API is not running.\n'
  exit 0
fi

pid="$(<"$pid_file")"
if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
  printf 'Invalid PID file. Removing %s.\n' "$pid_file" >&2
  rm -f "$pid_file"
  exit 1
fi

if ! kill -0 "$pid" 2>/dev/null; then
  if [[ -d "/proc/$pid" ]]; then
    printf 'Cannot manage the development API (PID %s) from this user session.\n' "$pid" >&2
    exit 1
  fi
  rm -f "$pid_file"
  printf 'Development API is not running.\n'
  exit 0
fi

kill -- "-$pid"
for _ in {1..10}; do
  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$pid_file"
    printf 'Development API stopped.\n'
    exit 0
  fi
  sleep 1
done

printf 'Development API did not stop gracefully; forcing shutdown.\n' >&2
kill -KILL -- "-$pid" 2>/dev/null || true
rm -f "$pid_file"
printf 'Development API stopped.\n'
