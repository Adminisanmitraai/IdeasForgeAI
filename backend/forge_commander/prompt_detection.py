from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

FORGE_COMMANDER_PROMPT_VERSION = "forge-commander.prompt-detection.v1"

PromptKind = Literal[
    "yes_no", "selection", "password",
    "confirmation", "unknown",
]

@dataclass(frozen=True, slots=True)
class DetectedPrompt:
    prompt_id: str
    kind: PromptKind
    text: str
    sensitive: bool
    options: tuple[str, ...] = ()

def _prompt_id(kind: PromptKind, text: str) -> str:
    digest = sha256(f"{kind}\n{text.strip()}".encode("utf-8")).hexdigest()[:20]
    return f"fc-prompt-{digest}"


def detect_prompt(text: str) -> DetectedPrompt | None:
    raw = text.strip()
    if not raw:
        return None
    lower = raw.lower()
    if "password" in lower or "passphrase" in lower:
        kind, sensitive, options = "password", True, ()
    elif "[y/n]" in lower or "(y/n)" in lower or "yes/no" in lower:
        kind, sensitive, options = "yes_no", False, ("y", "n")
    elif "select" in lower or "choose" in lower:
        kind, sensitive, options = "selection", False, ()
    elif "confirm" in lower or "are you sure" in lower or "continue?" in lower:
        kind, sensitive, options = "confirmation", False, ()
    else:
        return None
    return DetectedPrompt(_prompt_id(kind, raw), kind, raw, sensitive, options)
