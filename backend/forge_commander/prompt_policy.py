from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .prompt_detection import DetectedPrompt

FORGE_COMMANDER_PROMPT_POLICY_VERSION = "forge-commander.prompt-policy.v1"

PromptAction = Literal["auto_answer", "request_approval", "request_input", "block"]

@dataclass(frozen=True, slots=True)
class PromptDecision:
    action: PromptAction
    response: str | None
    reason: str
    approval_required: bool


def decide_prompt(prompt: DetectedPrompt, *, approved: bool = False) -> PromptDecision:
    if prompt.kind == "password":
        return PromptDecision("request_input", None, "secret_input_required", False)
    if prompt.sensitive and not approved:
        return PromptDecision("request_approval", None, "sensitive_prompt", True)
    if prompt.kind == "yes_no":
        return PromptDecision("auto_answer", "y", "safe_yes_no_default", False)
    if prompt.kind == "confirmation":
        return PromptDecision("request_approval", None, "confirmation_requires_review", True)
    if prompt.kind == "selection":
        return PromptDecision("request_input", None, "selection_requires_choice", False)
    return PromptDecision("block", None, "unsupported_prompt", False)


__all__ = [
    "FORGE_COMMANDER_PROMPT_POLICY_VERSION",
    "PromptAction", "PromptDecision", "decide_prompt",
]
