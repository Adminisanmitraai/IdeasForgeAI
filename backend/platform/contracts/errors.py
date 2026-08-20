from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

ERROR_CONTRACT_VERSION = "platform.error.v1"

ErrorCode = Literal[
    "VALIDATION_ERROR", "PERMISSION_DENIED", "APPROVAL_REQUIRED",
    "CAPABILITY_UNAVAILABLE", "DEPENDENCY_FAILED", "EXECUTION_FAILED",
    "VERIFICATION_FAILED", "TIMEOUT", "CANCELLED", "CONFLICT",
    "EXTERNAL_SERVICE_ERROR", "INTERNAL_ERROR",
]


@dataclass(frozen=True)
class PlatformError:
    code: ErrorCode
    message: str
    retryable: bool
    correlation_id: str
    safe_diagnostics: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = ERROR_CONTRACT_VERSION
