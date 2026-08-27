from __future__ import annotations

from dataclasses import dataclass

from .gui_policy import GuiActionRequest
from .intent_targeting import IntentRankedElement, TargetIntent
from .task_orchestrator import DesktopTaskStep

FORGE_COMMANDER_STEP_TARGET_RESOLVER_VERSION = "forge-commander.step-target-resolver.v1"

@dataclass(frozen=True, slots=True)
class StepTargetResolution:
    step_id: str
    resolved: bool
    reason: str
    candidate_element_id: str | None = None
    confidence: float = 0.0
    request: GuiActionRequest | None = None

def resolve_step_target(
    step: DesktopTaskStep, *, candidates: tuple[IntentRankedElement, ...],
    device_id: str, target_window_id: str,
    intent: TargetIntent = "page_content", min_score: float = 0.62,
    ambiguity_margin: float = 0.08,
) -> StepTargetResolution:
    if step.kind not in {"click", "type"}:
        return StepTargetResolution(step.step_id, False, "step_kind_not_targetable")
    if not candidates:
        return StepTargetResolution(step.step_id, False, "no_target_candidates")
    top = candidates[0]
    if top.intent_score < min_score:
        return StepTargetResolution(step.step_id, False, "target_confidence_too_low", top.ranked.element.element_id, top.intent_score)
    if len(candidates) > 1 and top.intent_score - candidates[1].intent_score < ambiguity_margin:
        return StepTargetResolution(step.step_id, False, "target_ambiguous", top.ranked.element.element_id, top.intent_score)
    element = top.ranked.element
    x, y = element.center
    action_type = "click" if step.kind == "click" else "type"
    request = GuiActionRequest(
        action_id=step.step_id,
        device_id=device_id,
        action_type=action_type,
        target_window_id=target_window_id,
        x=x if action_type == "click" else None,
        y=y if action_type == "click" else None,
        text=step.payload if action_type == "type" else None,
        required_authority="operational" if step.requires_approval else "safe_execute",
    )
    return StepTargetResolution(
        step.step_id, True, "target_resolved",
        element.element_id, top.intent_score, request,
    )

__all__ = [
    "FORGE_COMMANDER_STEP_TARGET_RESOLVER_VERSION",
    "StepTargetResolution", "resolve_step_target",
]
