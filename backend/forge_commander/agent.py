from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

FORGE_COMMANDER_AGENT_VERSION = "forge-commander.local-agent.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_state_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(root) / "IdeasForgeAI" / "ForgeCommander"


def write_local_presence(*, device_id: str, state_dir: Path) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "presence.json"
    payload = {
        "device_id": device_id,
        "state": "online",
        "heartbeat_at": _utc_now(),
        "agent_version": FORGE_COMMANDER_AGENT_VERSION,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

def main() -> int:
    parser = argparse.ArgumentParser(prog="forge-commander-agent")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--state-dir")
    parser.add_argument("--local-presence", action="store_true")
    args = parser.parse_args()

    if not args.local_presence:
        parser.error("only --local-presence is currently implemented")
    state_dir = Path(args.state_dir) if args.state_dir else default_state_dir()
    path = write_local_presence(device_id=args.device_id, state_dir=state_dir)
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
