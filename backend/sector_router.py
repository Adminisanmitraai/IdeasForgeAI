from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

from backend.sector_registry import SECTOR_REGISTRY, get_sector_entry


def _clean_text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, dict):
        return " ".join(_clean_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_clean_text(item) for item in value)
    return ""


def _keyword_present(lower_text: str, tokens: set[str], keyword: str) -> bool:
    normalized = keyword.lower().strip()
    if not normalized:
        return False
    if " " in normalized or "-" in normalized:
        return normalized in lower_text
    return normalized in tokens


def _matches(lower_text: str, tokens: set[str], keywords: Iterable[str]) -> List[str]:
    return [keyword for keyword in keywords if _keyword_present(lower_text, tokens, keyword)]


def _candidate_payload(sector_id: str, score: float, reasons: List[str]) -> Dict[str, Any]:
    entry = get_sector_entry(sector_id)
    return {
        "sector_id": sector_id,
        "display_name": entry["display_name"],
        "score": round(score, 3),
        "theme_family": entry["theme_family"],
        "layout_family": entry["layout_family"],
        "reasons": reasons[:6],
    }


def route_sector(
    idea_text: str,
    reference_image: Dict[str, Any] | None = None,
    locale_currency_metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_text = " ".join(
        part
        for part in [
            _clean_text(idea_text),
            _clean_text(reference_image or {}),
            _clean_text(locale_currency_metadata or {}),
        ]
        if part
    )
    lower_text = source_text.lower()
    tokens = set(re.findall(r"[a-z0-9]+", lower_text))
    candidates: List[Dict[str, Any]] = []

    for sector_id, entry in SECTOR_REGISTRY.items():
        strong = _matches(lower_text, tokens, entry["strong_keywords"])
        weak = _matches(lower_text, tokens, entry["weak_keywords"])
        negative = _matches(lower_text, tokens, entry["negative_keywords"])
        if sector_id == "agriculture_farmer" and "crop health" in lower_text:
            strong.append("crop health priority")
        if sector_id == "mutual_fund_advisor" and ("sip" in tokens or "mutual fund" in lower_text):
            strong.append("mutual fund/SIP priority")
        if sector_id == "clinic_healthcare" and any(term in lower_text for term in ["crop health", "farm health", "soil health"]):
            negative.append("crop/farm/soil health is agriculture")
        if sector_id == "insurance_broker" and ("sip" in tokens or "mutual fund" in lower_text):
            negative.append("mutual fund/SIP belongs to investment")

        priority_boost = entry["priority"] / 20 if strong or weak else 0
        score = len(strong) * 10 + len(weak) * 3 + priority_boost - len(negative) * 9
        if sector_id == "generic_saas":
            score = max(score, 1.0)
        reasons = [f"strong: {item}" for item in strong[:4]]
        reasons.extend(f"weak: {item}" for item in weak[:3])
        reasons.extend(f"negative: {item}" for item in negative[:3])
        candidates.append(_candidate_payload(sector_id, score, reasons))

    candidates.sort(key=lambda item: (item["score"], SECTOR_REGISTRY[item["sector_id"]]["priority"]), reverse=True)
    winner = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    confidence = max(0.0, min(0.99, winner["score"] / 36))
    close_score = bool(runner_up and winner["score"] - runner_up["score"] <= 4 and runner_up["score"] >= 8)
    low_confidence = confidence < 0.38 or winner["sector_id"] == "generic_saas"
    clarification_needed = low_confidence or close_score

    entry = get_sector_entry(winner["sector_id"])
    return {
        "sector_id": winner["sector_id"],
        "confidence": round(confidence, 3),
        "reasons": winner["reasons"],
        "top_candidates": candidates[:3],
        "theme_family": entry["theme_family"],
        "layout_family": entry["layout_family"],
        "clarification_needed": clarification_needed,
        "clarification_prompt": _clarification_prompt(candidates[:3]) if clarification_needed else "",
    }


def _clarification_prompt(candidates: List[Dict[str, Any]]) -> str:
    names = [candidate["display_name"] for candidate in candidates if candidate["sector_id"] != "generic_saas"]
    if not names:
        names = ["General SaaS"]
    if len(names) == 1:
        return f"I found one possible app type: {names[0]}. Is that correct?"
    return "I found multiple possible app types. Is this for " + ", ".join(names[:-1]) + f", or {names[-1]}?"


def validate_sector_routing_examples() -> Dict[str, str]:
    examples = {
        "farmer dashboard with crop health, mandi prices and weather": "agriculture_farmer",
        "insurance broker app for policy premium renewal and claim tracker": "insurance_broker",
        "mutual fund SIP advisor app with KYC risk profile and portfolio tracker": "mutual_fund_advisor",
        "school teacher app for homework attendance exam marks and parent messages": "school_teacher_parent",
        "clinic appointment app with doctor queue and patient follow ups": "clinic_healthcare",
        "car detailing doorstep booking and before after gallery": "car_detailing",
        "wedding lawn booking with haldi mehendi packages": "wedding_event_lawn",
        "restaurant ordering app with menu table booking and kitchen queue": "restaurant_food",
        "government citizen grievance app with officer dashboard and audit": "government_civic",
    }
    return {prompt: route_sector(prompt)["sector_id"] for prompt in examples}

