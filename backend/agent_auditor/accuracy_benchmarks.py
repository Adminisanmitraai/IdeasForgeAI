from __future__ import annotations

import argparse
import ast
import json
import py_compile
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]


CATEGORY_EXPECTATIONS = {
    "ui_and_visual_generation": {
        "keywords": ["ui", "layout", "screen", "style", "template", "html", "visual", "component"],
        "required_capability_fragments": ["ui", "layout", "visual", "template"],
    },
    "software_engineering": {
        "keywords": ["code", "patch", "file", "diff", "test", "project", "implementation"],
        "required_capability_fragments": ["code", "workflow", "engineering", "patch", "git"],
    },
    "data_persistence": {
        "keywords": ["data", "database", "schema", "storage", "persist", "record"],
        "required_capability_fragments": ["data", "storage", "persistence", "schema"],
    },
    "deployment_and_integration": {
        "keywords": ["deploy", "api", "frontend", "backend", "connector", "readiness", "release"],
        "required_capability_fragments": ["deployment", "integration", "api", "release"],
    },
    "professional_intelligence": {
        "keywords": ["expert", "profession", "workspace", "registry", "capability", "category"],
        "required_capability_fragments": ["expert", "registry", "professional", "workspace"],
    },
    "requirement_intake": {
        "keywords": ["idea", "prompt", "requirement", "intake", "scope", "clarify"],
        "required_capability_fragments": ["prompt", "requirement", "intake", "routing"],
    },
    "packaging": {
        "keywords": ["package", "mobile", "bundle", "export", "build"],
        "required_capability_fragments": ["package", "mobile", "build"],
    },
    "ui_pixel_mapping": {
        "keywords": ["pixel", "screenshot", "region", "composer", "card", "css", "layout"],
        "required_capability_fragments": ["pixel", "region", "screenshot", "layout"],
    },
    "general_agent": {
        "keywords": ["agent", "task", "result", "confidence", "output"],
        "required_capability_fragments": ["task", "output"],
    },
}


PIXEL_REQUIRED_METHODS = [
    "_detect_light_regions",
    "_estimate_composer_region",
    "_estimate_card_regions",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace").lstrip("\ufeff")


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def compile_and_parse(path: Path):
    py_compile.compile(str(path), doraise=True)
    source = read_text(path)
    return source, ast.parse(source)


def extract_symbols(tree: ast.AST) -> Dict[str, List[str]]:
    classes = []
    functions = []
    methods = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(child.name)

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    return {
        "classes": sorted(set(classes)),
        "functions": sorted(set(functions)),
        "methods": sorted(set(methods)),
    }


def text_hit_score(source: str, words: List[str], max_points: int) -> Dict[str, Any]:
    haystack = source.lower()
    hits = [word for word in words if word.lower() in haystack]

    if not words:
        score = max_points
    else:
        score = round((len(hits) / len(words)) * max_points, 2)

    return {
        "score": min(max_points, score),
        "hits": hits,
        "expected": words,
    }


def contract_quality_score(contract: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    checks = {}

    purpose = str(contract.get("purpose", "")).strip()
    capabilities = contract.get("capabilities", [])
    inputs = contract.get("required_inputs", [])
    outputs = contract.get("required_outputs", [])
    category = contract.get("registry_category")
    safety = contract.get("safety", {})

    checks["purpose_good"] = len(purpose) >= 30
    if checks["purpose_good"]:
        score += 15

    checks["capabilities_good"] = isinstance(capabilities, list) and len(capabilities) >= 2
    if checks["capabilities_good"]:
        score += 15

    checks["inputs_good"] = isinstance(inputs, list) and len(inputs) >= 1
    if checks["inputs_good"]:
        score += 10

    checks["outputs_good"] = isinstance(outputs, list) and len(outputs) >= 1
    if checks["outputs_good"]:
        score += 10

    checks["category_present"] = bool(category)
    if checks["category_present"]:
        score += 10

    checks["safety_present"] = isinstance(safety, dict) and bool(safety)
    if checks["safety_present"]:
        score += 10

    return {
        "score": score,
        "max_score": 70,
        "checks": checks,
    }


def category_alignment_score(source: str, contract: Dict[str, Any]) -> Dict[str, Any]:
    category = contract.get("registry_category") or "general_agent"
    expectations = CATEGORY_EXPECTATIONS.get(category, CATEGORY_EXPECTATIONS["general_agent"])

    keyword_result = text_hit_score(source, expectations["keywords"], 20)

    capability_text = " ".join(contract.get("capabilities", [])).lower()
    required_fragments = expectations["required_capability_fragments"]
    capability_hits = [frag for frag in required_fragments if frag in capability_text]

    capability_score = round((len(capability_hits) / max(1, len(required_fragments))) * 10, 2)

    return {
        "score": min(30, keyword_result["score"] + capability_score),
        "max_score": 30,
        "category": category,
        "keyword_hits": keyword_result["hits"],
        "keyword_expected": keyword_result["expected"],
        "capability_hits": capability_hits,
        "capability_expected": required_fragments,
    }


def pixel_specific_score(symbols: Dict[str, List[str]], source: str) -> Dict[str, Any]:
    all_symbols = set(symbols["functions"]) | set(symbols["methods"])
    method_hits = [name for name in PIXEL_REQUIRED_METHODS if name in all_symbols]

    score = round((len(method_hits) / len(PIXEL_REQUIRED_METHODS)) * 30, 2)

    extra_checks = {
        "uses_pillow_or_pil": "PIL" in source or "Image" in source or "pillow" in source.lower(),
        "mentions_composer": "composer" in source.lower(),
        "mentions_cards": "card" in source.lower(),
        "mentions_css": "css" in source.lower(),
    }

    for ok in extra_checks.values():
        if ok:
            score += 5

    return {
        "score": min(50, score),
        "max_score": 50,
        "required_methods": PIXEL_REQUIRED_METHODS,
        "method_hits": method_hits,
        "extra_checks": extra_checks,
    }


def generic_symbol_score(symbols: Dict[str, List[str]]) -> Dict[str, Any]:
    score = 0

    if symbols["classes"]:
        score += 20

    if symbols["functions"] or symbols["methods"]:
        score += 15

    return {
        "score": score,
        "max_score": 35,
        "symbols": symbols,
    }


def audit_accuracy(agent_path: Path, contract_path: Path | None = None) -> Dict[str, Any]:
    if not agent_path.exists():
        return {
            "ok": False,
            "overall_score": 0,
            "accuracy_score": 0,
            "grade": "Failing",
            "error": f"Agent file not found: {agent_path}",
        }

    contract = load_json(contract_path) if contract_path else {}

    if not contract:
        inferred_contract_path = ROOT / "backend" / "agent_auditor" / "contracts" / f"{agent_path.stem}.contract.json"
        contract = load_json(inferred_contract_path)

    try:
        source, tree = compile_and_parse(agent_path)
        symbols = extract_symbols(tree)
    except Exception as exc:
        return {
            "ok": False,
            "overall_score": 0,
            "accuracy_score": 0,
            "grade": "Failing",
            "error": str(exc),
        }

    contract_result = contract_quality_score(contract)
    category_result = category_alignment_score(source, contract)

    category = contract.get("registry_category") or "general_agent"

    if category == "ui_pixel_mapping" or "pixel" in agent_path.stem.lower():
        special_result = pixel_specific_score(symbols, source)
        raw_score = contract_result["score"] + category_result["score"] + special_result["score"]
        max_score = contract_result["max_score"] + category_result["max_score"] + special_result["max_score"]
    else:
        special_result = generic_symbol_score(symbols)
        raw_score = contract_result["score"] + category_result["score"] + special_result["score"]
        max_score = contract_result["max_score"] + category_result["max_score"] + special_result["max_score"]

    score = round((raw_score / max(1, max_score)) * 100, 2)

    if score >= 90:
        grade = "Excellent"
    elif score >= 80:
        grade = "Accurate baseline"
    elif score >= 70:
        grade = "Acceptable baseline"
    elif score >= 50:
        grade = "Weak baseline"
    else:
        grade = "Failing"

    return {
        "ok": score >= 70,
        "agent_file": str(agent_path.relative_to(ROOT)),
        "contract_file": str(contract_path.relative_to(ROOT)) if contract_path and contract_path.exists() else None,
        "overall_score": score,
        "accuracy_score": score,
        "grade": grade,
        "category": category,
        "contract_quality": contract_result,
        "category_alignment": category_result,
        "type_specific": special_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--contract")
    parser.add_argument("--fail-under", type=float, default=70)
    args = parser.parse_args()

    agent_path = (ROOT / args.agent).resolve()
    contract_path = (ROOT / args.contract).resolve() if args.contract else None

    result = audit_accuracy(agent_path, contract_path)

    print(json.dumps(result, indent=2))

    return 0 if result.get("accuracy_score", 0) >= args.fail_under else 1


if __name__ == "__main__":
    raise SystemExit(main())
