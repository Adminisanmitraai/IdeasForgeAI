# IdeasForgeAI Active Agent Registry Gate

The active registry must load only auditor-approved agents.

Rule:
Any weak, unaudited, missing-contract, smoke-test-failing, or blocked agent must not be loaded into runtime.

Required usage:
from backend.agent_auditor.active_agent_registry import require_approved_agent
require_approved_agent(agent_id='orchestrator_agent', min_score=75)

Safe import usage:
from backend.agent_auditor.active_agent_registry import safe_import_agent
module = safe_import_agent('pixel_matched_page_converter_agent', min_score=75)

Active registry map:
from backend.agent_auditor.active_agent_registry import build_active_registry
active_registry = build_active_registry(min_score=75)

Current gates:
- Compile gate
- Static smoke gate
- BOM-safe parser
- Agent contract gate
- Accuracy benchmark gate
- Active allowlist gate

New agent lifecycle:
Create agent -> add contract -> run auditor -> pass health and accuracy -> appear in allowlist -> load into runtime.
