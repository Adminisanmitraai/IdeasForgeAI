from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.product_flow import create_product_plan, resolve_currency_profile
from backend.sector_registry import get_sector_entry
from backend.sector_router import route_sector
from backend.sector_templates import create_sector_template
from backend.sector_test_cases import get_sector_test_cases


MIN_CONFIDENCE = 0.35


def _contains_all(container: List[str], required: List[str]) -> List[str]:
    normalized = {item.strip().lower() for item in container}
    return [item for item in required if item.strip().lower() not in normalized]


def _flatten_visible_text(value: Any) -> str:
    if isinstance(value, dict):
        hidden_keys = {
            "safety_rules",
            "forbidden_outputs",
            "forbidden_generic_terms",
            "trust_and_safety_notes",
            "compliance_notes",
        }
        return " ".join(
            _flatten_visible_text(item)
            for key, item in value.items()
            if str(key).strip().lower() not in hidden_keys
        )
    if isinstance(value, list):
        return " ".join(_flatten_visible_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _concept_text(plan: Dict[str, Any]) -> str:
    concept = plan.get("premium_ui_image_concept")
    return _flatten_visible_text(concept).lower() if isinstance(concept, dict) else ""


def _mockup_text(plan: Dict[str, Any]) -> str:
    mockup = plan.get("image_first_mockup")
    return _flatten_visible_text(mockup).lower() if isinstance(mockup, dict) else ""


def _case_result(case: Dict[str, Any]) -> Dict[str, Any]:
    prompt = case["prompt"]
    sector_result = route_sector(prompt)
    template = create_sector_template(sector_result, prompt)
    plan = create_product_plan(prompt)
    currency = resolve_currency_profile(prompt, {}, detected_domain=sector_result["sector_id"])
    entry = get_sector_entry(sector_result["sector_id"])
    failures: List[str] = []
    visible_text = f"{_flatten_visible_text(template)} {_flatten_visible_text(plan)}".lower()
    concept_text = _concept_text(plan)
    mockup_text = _mockup_text(plan)

    expected_sector = case["expected_sector_id"]
    if sector_result["sector_id"] != expected_sector:
        failures.append(f"expected sector {expected_sector}, got {sector_result['sector_id']}")

    forbidden = set(case.get("forbidden_sector_ids", []))
    winner_score = sector_result.get("top_candidates", [{}])[0].get("score", 0)
    forbidden_hits = [
        candidate["sector_id"]
        for candidate in sector_result.get("top_candidates", [])
        if candidate["sector_id"] in forbidden
        and candidate.get("score", 0) >= 8
        and candidate.get("reasons")
        and winner_score - candidate.get("score", 0) <= 4
    ]
    if sector_result["sector_id"] in forbidden:
        forbidden_hits.append(sector_result["sector_id"])
    if forbidden_hits:
        failures.append("forbidden sector appeared in winner/top candidates: " + ", ".join(sorted(set(forbidden_hits))))

    min_confidence = case.get("min_confidence", MIN_CONFIDENCE)
    if sector_result["confidence"] < min_confidence:
        failures.append(f"confidence {sector_result['confidence']} below minimum {min_confidence}")

    if sector_result["theme_family"] != case["expected_theme_family"]:
        failures.append(f"expected theme {case['expected_theme_family']}, got {sector_result['theme_family']}")

    expected_currency = case.get("expected_currency_code")
    if expected_currency and currency["currency_code"] != expected_currency:
        failures.append(f"expected currency {expected_currency}, got {currency['currency_code']}")

    if "expected_clarification_needed" in case and sector_result["clarification_needed"] != case["expected_clarification_needed"]:
        failures.append(
            f"expected clarification_needed {case['expected_clarification_needed']}, got {sector_result['clarification_needed']}"
        )

    missing_screens = _contains_all(template.get("screens", []), case.get("required_screens", []))
    if missing_screens:
        failures.append("missing template screens: " + ", ".join(missing_screens))

    forbidden_terms = [
        term for term in case.get("forbidden_visible_terms", [])
        if term.strip().lower() in visible_text
    ]
    if forbidden_terms:
        failures.append("forbidden visible terms appeared: " + ", ".join(forbidden_terms))

    required_terms = [
        term for term in case.get("required_visible_terms", [])
        if term.strip().lower() not in visible_text
    ]
    if required_terms:
        failures.append("missing required visible terms: " + ", ".join(required_terms))

    if case.get("requires_image_first_mockup") and not isinstance(plan.get("image_first_mockup"), dict):
        failures.append("missing image_first_mockup")

    if case.get("requires_premium_ui_image_concept") and not isinstance(plan.get("premium_ui_image_concept"), dict):
        failures.append("missing premium_ui_image_concept")

    missing_concept_terms = [
        term for term in case.get("required_concept_terms", [])
        if term.strip().lower() not in concept_text
    ]
    if missing_concept_terms:
        failures.append("missing concept terms: " + ", ".join(missing_concept_terms))

    forbidden_concept_terms = [
        term for term in case.get("forbidden_concept_terms", [])
        if term.strip().lower() in concept_text
    ]
    if forbidden_concept_terms:
        failures.append("forbidden concept terms appeared: " + ", ".join(forbidden_concept_terms))

    missing_mockup_terms = [
        term for term in case.get("required_mockup_terms", [])
        if term.strip().lower() not in mockup_text
    ]
    if missing_mockup_terms:
        failures.append("missing mockup terms: " + ", ".join(missing_mockup_terms))

    forbidden_mockup_terms = [
        term for term in case.get("forbidden_mockup_terms", [])
        if term.strip().lower() in mockup_text
    ]
    if forbidden_mockup_terms:
        failures.append("forbidden mockup terms appeared: " + ", ".join(forbidden_mockup_terms))

    aliases = template.get("clickable_aliases", {})
    missing_aliases = [alias for alias in case.get("required_aliases", []) if alias not in aliases]
    if missing_aliases:
        failures.append("missing clickable aliases: " + ", ".join(missing_aliases))

    safety_text = " ".join(entry.get("safety_rules", []) + entry.get("forbidden_outputs", [])).lower()
    missing_safety = [
        expectation
        for expectation in case.get("safety_expectations", [])
        if not any(token in safety_text for token in expectation.lower().split() if len(token) > 3)
    ]
    if missing_safety:
        failures.append("missing safety expectations: " + ", ".join(missing_safety))

    return {
        "test_id": case["test_id"],
        "ok": not failures,
        "failures": failures,
        "sector_id": sector_result["sector_id"],
        "confidence": sector_result["confidence"],
        "theme_family": sector_result["theme_family"],
        "currency_code": currency["currency_code"],
        "clarification_needed": sector_result["clarification_needed"],
    }


def run_sector_qa() -> Dict[str, Any]:
    cases = get_sector_test_cases()
    results = [_case_result(case) for case in cases]
    failures = [result for result in results if not result["ok"]]
    return {
        "ok": not failures,
        "total": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "results": results,
        "failures": failures,
    }


def main() -> int:
    report = run_sector_qa()
    print("IdeasForgeAI Sector QA")
    print(f"Total: {report['total']} | Passed: {report['passed']} | Failed: {report['failed']}")
    for result in report["results"]:
        status = "PASS" if result["ok"] else "FAIL"
        line = (
            f"{status} {result['test_id']} -> {result['sector_id']} "
            f"(confidence={result['confidence']}, theme={result['theme_family']}, currency={result['currency_code']})"
        )
        print(line)
        for failure in result["failures"]:
            print(f"  - {failure}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
