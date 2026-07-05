from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "backend" / "agents"
CONTRACTS_DIR = ROOT / "backend" / "agent_auditor" / "contracts"


def is_agent_file(path: Path) -> bool:
    name = path.name.lower()

    if path.suffix != ".py":
        return False

    if name == "__init__.py":
        return False

    ignored = [
        ".before-",
        ".backup",
        ".bak",
        ".old",
        ".tmp",
        "test_",
        "_test",
    ]

    return not any(item in name for item in ignored)


def title_from_stem(stem: str) -> str:
    return stem.replace("_", " ").title()


def category_from_name(stem: str) -> str:
    name = stem.lower()

    if "pixel" in name or "visual" in name or "ui" in name or "template" in name or "html" in name:
        return "ui_and_visual_generation"

    if "code" in name or "git" in name or "runtime" in name or "orchestrator" in name:
        return "software_engineering"

    if "database" in name or "persistence" in name:
        return "data_persistence"

    if "deployment" in name or "frontend_api" in name or "connector" in name:
        return "deployment_and_integration"

    if "expert" in name or "forgework" in name:
        return "professional_intelligence"

    if "prompt" in name or "idea" in name or "intake" in name:
        return "requirement_intake"

    if "package" in name:
        return "packaging"

    return "general_agent"


def capabilities_from_name(stem: str) -> List[str]:
    name = stem.lower()
    caps = []

    if "pixel" in name:
        caps += ["screenshot_analysis", "pixel_region_detection", "layout_mapping"]

    if "ui" in name or "visual" in name:
        caps += ["ui_generation", "visual_layout_planning"]

    if "code" in name:
        caps += ["code_generation", "code_patch_planning"]

    if "git" in name:
        caps += ["version_control_analysis", "git_status_review"]

    if "database" in name or "persistence" in name:
        caps += ["data_storage_planning", "persistence_validation"]

    if "deployment" in name:
        caps += ["deployment_readiness_check", "release_validation"]

    if "orchestrator" in name:
        caps += ["agent_coordination", "workflow_routing"]

    if "prompt" in name:
        caps += ["prompt_structuring", "requirement_expansion"]

    if "template" in name:
        caps += ["template_selection", "page_structure_generation"]

    if "mobile" in name:
        caps += ["mobile_package_planning", "app_build_preparation"]

    if "forgework" in name or "expert" in name:
        caps += ["expert_registry_support", "professional_workspace_logic"]

    if not caps:
        caps = ["task_execution", "structured_output_generation"]

    return sorted(set(caps))


def input_output_from_name(stem: str) -> Dict[str, List[str]]:
    name = stem.lower()

    if "pixel" in name:
        return {
            "required_inputs": ["screenshot", "target_ui_requirement"],
            "required_outputs": ["detected_regions", "composer_region", "card_regions", "css_variables", "confidence"]
        }

    if "code" in name:
        return {
            "required_inputs": ["project_context", "user_requirement"],
            "required_outputs": ["implementation_plan", "code_changes", "validation_notes"]
        }

    if "git" in name:
        return {
            "required_inputs": ["repository_path"],
            "required_outputs": ["git_status_summary", "safe_commit_guidance"]
        }

    if "database" in name or "persistence" in name:
        return {
            "required_inputs": ["data_model", "storage_requirement"],
            "required_outputs": ["persistence_plan", "schema_or_storage_result"]
        }

    if "deployment" in name:
        return {
            "required_inputs": ["project_status", "deployment_target"],
            "required_outputs": ["readiness_report", "blocking_issues", "release_recommendation"]
        }

    if "template" in name:
        return {
            "required_inputs": ["page_type", "brand_context", "layout_requirement"],
            "required_outputs": ["selected_template", "layout_plan", "implementation_notes"]
        }

    if "ui" in name or "visual" in name or "html" in name:
        return {
            "required_inputs": ["brand_context", "screen_requirement"],
            "required_outputs": ["ui_plan", "layout_structure", "style_guidance"]
        }

    if "prompt" in name or "idea" in name or "intake" in name:
        return {
            "required_inputs": ["raw_user_idea"],
            "required_outputs": ["structured_requirement", "clarified_scope", "agent_routing_plan"]
        }

    if "orchestrator" in name:
        return {
            "required_inputs": ["user_request", "available_agents"],
            "required_outputs": ["selected_agent", "execution_plan", "approval_requirements"]
        }

    return {
        "required_inputs": ["task_requirement"],
        "required_outputs": ["agent_result", "confidence", "notes"]
    }


def purpose_from_name(stem: str) -> str:
    title = title_from_stem(stem)
    category = category_from_name(stem).replace("_", " ")

    return (
        f"{title} supports the IdeasForgeAI {category} workflow by accepting structured task requirements, "
        f"performing the agent-specific operation, and returning safe, reviewable, production-oriented output."
    )


def build_contract(path: Path) -> Dict:
    stem = path.stem
    io = input_output_from_name(stem)

    contract = {
        "agent_id": stem,
        "name": title_from_stem(stem),
        "version": "0.1.0",
        "purpose": purpose_from_name(stem),
        "registry_category": category_from_name(stem),
        "capabilities": capabilities_from_name(stem),
        "required_inputs": io["required_inputs"],
        "required_outputs": io["required_outputs"],
        "minimum_health_score": 75,
        "smoke_tests": [
            {
                "name": "import-smoke-test",
                "command": f"python backend\\agent_auditor\\smoke_import_agent.py --agent backend\\agents\\{path.name}",
                "timeout_seconds": 30
            }
        ],
        "safety": {
            "requires_approval": True,
            "allowed_actions": [
                "analyze_input",
                "generate_structured_output",
                "write_agent_report"
            ],
            "blocked_actions": [
                "unapproved_live_execution",
                "blind_file_patch",
                "stage_unrelated_files",
                "use_screenshot_as_background"
            ]
        }
    }

    if "pixel" in stem.lower():
        contract["accuracy_method"] = "pixel_region_iou"
        contract["minimum_accuracy_score"] = 70

    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

    agent_files = sorted([p for p in AGENTS_DIR.rglob("*.py") if is_agent_file(p)])

    created = []
    skipped = []
    overwritten = []

    for path in agent_files:
        contract_path = CONTRACTS_DIR / f"{path.stem}.contract.json"

        if contract_path.exists() and not args.force:
            skipped.append(str(contract_path.relative_to(ROOT)))
            continue

        contract = build_contract(path)

        if args.write:
            existed = contract_path.exists()
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

            if existed:
                overwritten.append(str(contract_path.relative_to(ROOT)))
            else:
                created.append(str(contract_path.relative_to(ROOT)))

    result = {
        "ok": True,
        "agent_count": len(agent_files),
        "created": created,
        "overwritten": overwritten,
        "skipped": skipped,
        "write": args.write,
        "force": args.force
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
