#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

stop_pid_file() {
  local pid_file="$1"

  if [ -f "$pid_file" ]; then
    local pid
    pid="$(cat "$pid_file")"

    if [ -n "$pid" ] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi

    rm -f "$pid_file"
  fi
}

stop_pid_file .logs/backend.pid
stop_pid_file .logs/frontend.pid

pkill -f "uvicorn.*backend.main:app" >/dev/null 2>&1 || true
pkill -f "http.server 8088" >/dev/null 2>&1 || true

echo "IdeasForgeAI dev processes stopped."
