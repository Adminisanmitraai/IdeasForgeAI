#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .logs

bash scripts/dev-stop.sh >/dev/null 2>&1 || true

nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > .logs/backend.log 2>&1 &
echo "$!" > .logs/backend.pid

nohup python -m http.server 8088 --bind 0.0.0.0 > .logs/frontend.log 2>&1 &
echo "$!" > .logs/frontend.pid

echo "Backend running on port 8000"
echo "Frontend running on port 8088"
echo "Open frontend preview from Codespaces PORTS tab"
