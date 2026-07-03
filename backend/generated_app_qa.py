from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List


QA_RULE_IDS = [
    "no_raw_runtime_api_visible",
    "no_large_data_model_section",
    "no_large_api_ready_section",
    "no_large_backend_proxy_placeholder_section",
    "no_large_monetization_section_without_request",
    "required_screens_exist",
    "required_clickable_aliases_exist",
    "required_visible_terms_exist",
    "forbidden_visible_terms_absent",
    "no_generic_crm_fallback_for_specific_sector",
    "no_fake_policy_certificate_document_language",
    "no_guaranteed_returns_for_investments",
]

DEVELOPER_SECTION_TERMS = {
    "Data Model": "no_large_data_model_section",
    "API Ready": "no_large_api_ready_section",
    "Backend proxy placeholders": "no_large_backend_proxy_placeholder_section",
}

FAKE_DOCUMENT_PATTERNS = [
    r"\bfake\s+(policy|certificate|document|approval|kyc|claim)\b",
    r"\bgenerate\s+(official\s+)?(certificate|government document|policy)\b",
    r"\bauto[- ]?approve\s+(claim|kyc|certificate|document)\b",
]

GENERIC_CRM_TERMS = ["generic crm", "crm fallback", "active users", "open tasks", "sales pipeline"]
INVESTMENT_SECTOR_IDS = {"mutual_fund_advisor"}
SPECIFIC_SECTOR_EXEMPTIONS = {"generic_saas"}


def flatten_generated_output(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    try:
        return json.dumps(output, ensure_ascii=False, default=str)
    except TypeError:
        return str(output)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _contains_alias(text: str, alias: str) -> bool:
    normalized_alias = _normalize(alias).replace("_", " ")
    normalized_text = _normalize(text).replace("_", " ")
    compact_alias = re.sub(r"[^a-z0-9]+", "", normalized_alias)
    compact_text = re.sub(r"[^a-z0-9]+", "", normalized_text)
    return normalized_alias in normalized_text or compact_alias in compact_text


def _result(rule_id: str, passed: bool, message: str) -> Dict[str, Any]:
    return {"rule_id": rule_id, "passed": passed, "message": message}


def check_generated_app_output(
    output: Any,
    *,
    sector_id: str = "generic_saas",
    required_screens: Iterable[str] | None = None,
    required_aliases: Iterable[str] | None = None,
    required_terms: Iterable[str] | None = None,
    forbidden_terms: Iterable[str] | None = None,
    user_prompt: str = "",
) -> Dict[str, Any]:
    text = flatten_generated_output(output)
    lower_text = _normalize(text)
    lower_prompt = _normalize(user_prompt)
    checks: List[Dict[str, Any]] = []

    checks.append(
        _result(
            "no_raw_runtime_api_visible",
            "/api/runtime/" not in lower_text,
            "Generated UI must not expose raw /api/runtime/ URLs.",
        )
    )

    for label, rule_id in DEVELOPER_SECTION_TERMS.items():
        checks.append(
            _result(
                rule_id,
                label.lower() not in lower_text,
                f"Generated UI must not show a large developer-only {label} section.",
            )
        )

    monetization_requested = any(term in lower_prompt for term in ["monetization", "pricing", "subscription", "revenue model"])
    checks.append(
        _result(
            "no_large_monetization_section_without_request",
            monetization_requested or "monetization" not in lower_text,
            "Generated UI must not show a large Monetization section unless the user asked for it.",
        )
    )

    missing_screens = [screen for screen in required_screens or [] if not _contains_alias(text, str(screen))]
    checks.append(
        _result(
            "required_screens_exist",
            not missing_screens,
            "Missing required screens: " + ", ".join(missing_screens) if missing_screens else "All required screens are present.",
        )
    )

    missing_aliases = [alias for alias in required_aliases or [] if not _contains_alias(text, str(alias))]
    checks.append(
        _result(
            "required_clickable_aliases_exist",
            not missing_aliases,
            "Missing clickable aliases: " + ", ".join(missing_aliases) if missing_aliases else "All required aliases are present.",
        )
    )

    missing_terms = [term for term in required_terms or [] if not _contains_alias(text, str(term))]
    checks.append(
        _result(
            "required_visible_terms_exist",
            not missing_terms,
            "Missing required visible terms: " + ", ".join(missing_terms) if missing_terms else "All required visible terms are present.",
        )
    )

    found_forbidden_terms = [term for term in forbidden_terms or [] if _contains_alias(text, str(term))]
    checks.append(
        _result(
            "forbidden_visible_terms_absent",
            not found_forbidden_terms,
            "Forbidden visible terms appeared: " + ", ".join(found_forbidden_terms) if found_forbidden_terms else "No forbidden visible terms found.",
        )
    )

    generic_fallback_found = any(term in lower_text for term in GENERIC_CRM_TERMS)
    checks.append(
        _result(
            "no_generic_crm_fallback_for_specific_sector",
            sector_id in SPECIFIC_SECTOR_EXEMPTIONS or not generic_fallback_found,
            "Specific sectors must not fall back to generic CRM copy.",
        )
    )

    fake_language_found = any(re.search(pattern, lower_text) for pattern in FAKE_DOCUMENT_PATTERNS)
    checks.append(
        _result(
            "no_fake_policy_certificate_document_language",
            not fake_language_found,
            "Generated app must not include fake policy, certificate, approval, KYC, claim, or document language.",
        )
    )

    investment_sector = sector_id in INVESTMENT_SECTOR_IDS or any(term in lower_prompt for term in ["mutual fund", "sip", "investment"])
    guaranteed_return_found = any(term in lower_text for term in ["guaranteed returns", "guaranteed return", "promised profit", "assured profit"])
    checks.append(
        _result(
            "no_guaranteed_returns_for_investments",
            not investment_sector or not guaranteed_return_found,
            "Investment and mutual fund apps must not promise guaranteed returns or profit.",
        )
    )

    failures = [check for check in checks if not check["passed"]]
    return {
        "ok": not failures,
        "sector_id": sector_id,
        "checks": checks,
        "failures": failures,
        "summary": f"{len(checks) - len(failures)} passed, {len(failures)} failed",
    }


def assert_generated_app_output(
    output: Any,
    *,
    sector_id: str = "generic_saas",
    required_screens: Iterable[str] | None = None,
    required_aliases: Iterable[str] | None = None,
    required_terms: Iterable[str] | None = None,
    forbidden_terms: Iterable[str] | None = None,
    user_prompt: str = "",
) -> Dict[str, Any]:
    report = check_generated_app_output(
        output,
        sector_id=sector_id,
        required_screens=required_screens,
        required_aliases=required_aliases,
        required_terms=required_terms,
        forbidden_terms=forbidden_terms,
        user_prompt=user_prompt,
    )
    if not report["ok"]:
        messages = "; ".join(failure["message"] for failure in report["failures"])
        raise AssertionError(messages)
    return report
