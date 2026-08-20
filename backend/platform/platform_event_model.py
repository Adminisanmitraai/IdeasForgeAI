from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

CONTRACT_VERSION = "platform.event-envelope.v1"
MAX_PAYLOAD_BYTES = 32768
MAX_METADATA_BYTES = 16384


@dataclass(frozen=True)
class PlatformEvent:
    event_id: str
    event_type: str
    source: str
    occurred_at: str
    correlation_id: str
    causation_id: str = ""
    sequence: int = 0
    subject_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    contract_version: str = CONTRACT_VERSION


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _bounded_mapping(value: Mapping[str, Any], maximum_bytes: int) -> dict[str, Any]:
    output = {str(k): v for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    encoded = _canonical_json(output).encode("utf-8")
    if len(encoded) <= maximum_bytes:
        return output
    return {"truncated": True, "sha256": hashlib.sha256(encoded).hexdigest()}


def build_event(
    *, event_type: str, source: str, occurred_at: str, correlation_id: str,
    causation_id: str = "", sequence: int = 0, subject_id: str = "",
    payload: Mapping[str, Any] | None = None, metadata: Mapping[str, Any] | None = None,
) -> PlatformEvent:
    if not all(str(v).strip() for v in (event_type, source, occurred_at, correlation_id)):
        raise ValueError("event_type, source, occurred_at and correlation_id are required")
    core = {
        "event_type": event_type, "source": source, "occurred_at": occurred_at,
        "correlation_id": correlation_id, "causation_id": causation_id,
        "sequence": int(sequence), "subject_id": subject_id,
        "payload": _bounded_mapping(payload or {}, MAX_PAYLOAD_BYTES),
        "metadata": _bounded_mapping(metadata or {}, MAX_METADATA_BYTES),
    }
    digest = hashlib.sha256(_canonical_json(core).encode("utf-8")).hexdigest()[:24]
    return PlatformEvent(event_id=f"evt-{digest}", **core)

def from_terminal_session_event(event: Any, *, execution_id: str, occurred_at: str) -> PlatformEvent:
    event_type = str(getattr(event, "event_type", "event"))
    return build_event(
        event_type=f"terminal.{event_type}", source="forgecode.terminal",
        occurred_at=occurred_at, correlation_id=execution_id,
        sequence=int(getattr(event, "sequence", 0)), subject_id=execution_id,
        payload={
            "status": str(getattr(event, "status", "")),
            "step_id": str(getattr(event, "step_id", "")),
            "stream": str(getattr(event, "stream", "")),
            "payload": str(getattr(event, "payload", "")),
        },
        metadata=dict(getattr(event, "metadata", {}) or {}),
    )


def from_chat_delta(*, correlation_id: str, sequence: int, text: str, occurred_at: str) -> PlatformEvent:
    return build_event(
        event_type="chat.delta", source="ideasforge.chat", occurred_at=occurred_at,
        correlation_id=correlation_id, sequence=sequence, subject_id=correlation_id,
        payload={"text": text},
    )


def serialize_event(event: PlatformEvent) -> dict[str, Any]:
    return asdict(event)


__all__ = [
    "CONTRACT_VERSION", "PlatformEvent", "build_event", "from_terminal_session_event",
    "from_chat_delta", "serialize_event",
]
