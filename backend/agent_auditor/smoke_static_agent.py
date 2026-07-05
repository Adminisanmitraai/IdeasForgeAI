from __future__ import annotations

import argparse
import ast
import json
import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, help="Agent file path")
    args = parser.parse_args()

    path = (ROOT / args.agent).resolve()

    result = {
        "ok": False,
        "agent_file": str(path.relative_to(ROOT)) if path.exists() else str(path),
        "compile_ok": False,
        "ast_ok": False,
        "classes": [],
        "functions": [],
        "assignments": [],
        "has_agent_contract": False,
        "source_lines": 0,
        "error": None,
    }

    try:
        if not path.exists():
            raise FileNotFoundError(f"Agent file not found: {path}")

        py_compile.compile(str(path), doraise=True)
        result["compile_ok"] = True

        source = path.read_text(encoding="utf-8-sig", errors="replace").lstrip("\ufeff")
        result["source_lines"] = len(source.splitlines())

        tree = ast.parse(source)
        result["ast_ok"] = True

        classes = []
        functions = []
        assignments = []
        has_contract = False

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments.append(target.id)
                        if target.id == "AGENT_CONTRACT":
                            has_contract = True

            if isinstance(node, ast.AnnAssign):
                target = node.target
                if isinstance(target, ast.Name):
                    assignments.append(target.id)
                    if target.id == "AGENT_CONTRACT":
                        has_contract = True

        result["classes"] = classes
        result["functions"] = functions
        result["assignments"] = assignments
        result["has_agent_contract"] = has_contract

        has_structure = (
            len(classes) > 0
            or len(functions) > 0
            or len(assignments) > 0
            or result["source_lines"] >= 5
        )

        result["ok"] = result["compile_ok"] and result["ast_ok"] and has_structure

        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    except Exception as exc:
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
