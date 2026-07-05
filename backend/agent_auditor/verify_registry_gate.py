from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.agent_auditor.active_agent_registry import (
    ActiveAgentRegistryError,
    build_active_registry,
    registry_summary,
    require_approved_agent,
    safe_import_agent,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify IdeasForgeAI active agent registry gate.")
    parser.add_argument("--summary", action="store_true", help="Print active registry summary.")
    parser.add_argument("--agent", help="Verify one approved agent by id.")
    parser.add_argument("--import-agent", help="Try safe importing one approved agent by id.")
    parser.add_argument("--min-score", type=float, default=75)
    args = parser.parse_args()

    try:
        if args.summary:
            print(json.dumps(registry_summary(min_score=args.min_score), indent=2))
            return 0

        if args.agent:
            agent = require_approved_agent(agent_id=args.agent, min_score=args.min_score)
            print(json.dumps({
                "ok": True,
                "message": "Agent is approved for active registry loading.",
                "agent": agent,
            }, indent=2))
            return 0

        if args.import_agent:
            module = safe_import_agent(args.import_agent, min_score=args.min_score)
            print(json.dumps({
                "ok": True,
                "message": "Agent passed registry gate and imported successfully.",
                "agent_id": args.import_agent,
                "module": getattr(module, "__name__", None),
            }, indent=2))
            return 0

        registry = build_active_registry(min_score=args.min_score)

        print(json.dumps({
            "ok": True,
            "active_registry_count": len(registry),
            "active_agent_ids": sorted(registry.keys()),
        }, indent=2))

        return 0

    except ActiveAgentRegistryError as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
        }, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
