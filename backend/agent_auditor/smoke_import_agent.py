from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def module_name_from_path(path: Path) -> str:
    relative = path.resolve().relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, help="Agent file path")
    args = parser.parse_args()

    path = (ROOT / args.agent).resolve()

    if not path.exists():
        print(json.dumps({
            "ok": False,
            "error": f"Agent file not found: {path}"
        }, indent=2))
        return 1

    module_name = module_name_from_path(path)

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not create module spec.")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        classes = [
            name for name, value in vars(module).items()
            if isinstance(value, type)
        ]

        print(json.dumps({
            "ok": True,
            "agent_file": str(path.relative_to(ROOT)),
            "module_name": module_name,
            "classes": classes,
            "has_agent_contract": hasattr(module, "AGENT_CONTRACT")
        }, indent=2))

        return 0

    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "agent_file": str(path.relative_to(ROOT)),
            "module_name": module_name,
            "error": str(exc)
        }, indent=2))

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
