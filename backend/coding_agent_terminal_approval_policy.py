from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

CONTRACT_VERSION = "forgecode.terminal-approval-policy.v1"
AUDIT_CONTRACT_VERSION = "forgecode.terminal-audit.v1"
SESSION_CONTRACT_VERSION = "forgecode.terminal-session.v1"
RUNTIME_CONTRACT_VERSION = "forgecode.terminal-runtime.v1"

_ALLOWED_RISKS = {"low", "medium", "high", "critical"}
_ALLOWED_ROLES = {"viewer", "developer", "maintainer", "admin", "founder"}
_ROLE_RANK = {"viewer": 0, "developer": 1, "maintainer": 2, "admin": 3, "founder": 4}
_RISK_MIN_ROLE = {"low": "developer", "medium": "maintainer", "high": "admin", "critical": "founder"}
_TERMINAL_STATES = {"approved", "denied", "expired", "revoked", "consumed", "invalid"}

@dataclass(frozen=True)
class TerminalApprovalCapabilities:
    approval_issue: bool = True
    approval_verify: bool = True
    approval_revoke: bool = True
    replay_protection: bool = True
    role_enforcement: bool = True
    risk_enforcement: bool = True
    deterministic_serialization: bool = True
    audit_decisions: bool = True
    command_execution: bool = False
    background_execution: bool = False
    shell: bool = False
    file_write: bool = False
    database: bool = False
    git_read: bool = False
    git_write: bool = False
    network: bool = False
    deployment: bool = False
    api_routes: bool = False

@dataclass(frozen=True)
class TerminalApprovalPolicy:
    issuer: str = "forgecode"
    audience: str = "forgecode-terminal"
    default_ttl_seconds: int = 300
    maximum_ttl_seconds: int = 1800
    clock_skew_seconds: int = 5
    require_one_time_use: bool = True
    require_session_binding: bool = True
    require_project_binding: bool = True
    require_command_binding: bool = True
    allow_critical: bool = False
    minimum_role_by_risk: dict[str, str] = field(
        default_factory=lambda: dict(_RISK_MIN_ROLE)
    )
    allowed_roles: tuple[str, ...] = tuple(sorted(_ALLOWED_ROLES))
    max_active_tokens: int = 2048
    max_revoked_tokens: int = 4096
    max_consumed_tokens: int = 4096
    max_decisions: int = 8192

@dataclass(frozen=True)
class TerminalApprovalRequest:
    subject: str
    role: str
    project_id: str
    plan_sha256: str
    command_id: str
    session_id: str
    risk: str
    requested_at: int
    expires_at: int | None = None
    approval_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TerminalApprovalClaims:
    token_id: str
    issuer: str
    audience: str
    subject: str
    role: str
    project_id: str
    plan_sha256: str
    command_id: str
    session_id: str
    risk: str
    issued_at: int
    not_before: int
    expires_at: int
    one_time_use: bool
    approval_reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TerminalApprovalToken:
    token: str
    token_id: str
    expires_at: int
    claims_sha256: str

@dataclass(frozen=True)
class TerminalApprovalContext:
    now: int
    subject: str
    role: str
    project_id: str
    plan_sha256: str
    command_id: str
    session_id: str
    risk: str

@dataclass(frozen=True)
class TerminalApprovalDecision:
    ok: bool
    state: str
    code: str
    message: str
    token_id: str = ""
    claims_sha256: str = ""
    decision_sha256: str = ""
    consumed: bool = False
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

class TerminalApprovalValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

def _b64d(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))

def _validate_hash(name: str, value: str) -> str:
    text = str(value).lower()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise TerminalApprovalValidationError("invalid_hash", f"{name} must be a lowercase SHA-256 hex digest.")
    return text

def _validate_text(name: str, value: str, *, maximum: int = 256) -> str:
    text = str(value).strip()
    if not text:
        raise TerminalApprovalValidationError("validation_failed", f"{name} is required.")
    if len(text) > maximum:
        raise TerminalApprovalValidationError("validation_failed", f"{name} is too long.")
    if any(ord(ch) < 32 for ch in text):
        raise TerminalApprovalValidationError("validation_failed", f"{name} contains control characters.")
    return text

def _sanitize_metadata(value: Mapping[str, Any] | None, *, max_items: int = 32) -> dict[str, Any]:
    if not value:
        return {}
    output: dict[str, Any] = {}
    for index, key in enumerate(sorted(value)):
        if index >= max_items:
            break
        key_text = _validate_text("metadata key", str(key), maximum=80)
        item = value[key]
        if item is None or isinstance(item, (bool, int, float)):
            output[key_text] = item
        elif isinstance(item, str):
            output[key_text] = item[:512]
        elif isinstance(item, (list, tuple)):
            output[key_text] = [str(part)[:128] for part in list(item)[:16]]
        else:
            output[key_text] = str(item)[:512]
    return output

def terminal_approval_request_sha256(request: TerminalApprovalRequest) -> str:
    payload = asdict(request)
    payload["metadata"] = _sanitize_metadata(request.metadata)
    return _sha256_text(_canonical_json(payload))

def terminal_approval_claims_sha256(claims: TerminalApprovalClaims) -> str:
    payload = asdict(claims)
    payload["metadata"] = _sanitize_metadata(claims.metadata)
    return _sha256_text(_canonical_json(payload))

def terminal_approval_decision_sha256(decision: TerminalApprovalDecision) -> str:
    payload = asdict(decision)
    payload["decision_sha256"] = ""
    payload["metadata"] = _sanitize_metadata(decision.metadata)
    return _sha256_text(_canonical_json(payload))

def serialize_terminal_approval_decision(decision: TerminalApprovalDecision) -> dict[str, Any]:
    payload = asdict(decision)
    payload["warnings"] = list(decision.warnings)
    return payload

def terminal_approval_decision_json(decision: TerminalApprovalDecision) -> str:
    return _canonical_json(serialize_terminal_approval_decision(decision))

def _decision(
    ok: bool,
    state: str,
    code: str,
    message: str,
    *,
    token_id: str = "",
    claims_sha256: str = "",
    consumed: bool = False,
    warnings: Iterable[str] = (),
    metadata: Mapping[str, Any] | None = None,
) -> TerminalApprovalDecision:
    if state not in _TERMINAL_STATES:
        raise TerminalApprovalValidationError("validation_failed", "Unknown approval decision state.")
    draft = TerminalApprovalDecision(
        ok=ok,
        state=state,
        code=code,
        message=message,
        token_id=token_id,
        claims_sha256=claims_sha256,
        consumed=consumed,
        warnings=tuple(sorted(set(warnings))),
        metadata=_sanitize_metadata(metadata),
    )
    return TerminalApprovalDecision(**(asdict(draft) | {"decision_sha256": terminal_approval_decision_sha256(draft)}))

def _required_role(policy: TerminalApprovalPolicy, risk: str) -> str:
    value = policy.minimum_role_by_risk.get(risk)
    if value not in _ROLE_RANK:
        raise TerminalApprovalValidationError("invalid_policy", f"No valid minimum role configured for risk {risk}.")
    return value

def _authorize_role(policy: TerminalApprovalPolicy, role: str, risk: str) -> None:
    if role not in policy.allowed_roles or role not in _ROLE_RANK:
        raise TerminalApprovalValidationError("role_not_allowed", "Role is not allowed by policy.")
    required = _required_role(policy, risk)
    if _ROLE_RANK[role] < _ROLE_RANK[required]:
        raise TerminalApprovalValidationError("insufficient_role", f"Risk {risk} requires role {required} or higher.")
    if risk == "critical" and not policy.allow_critical:
        raise TerminalApprovalValidationError("critical_not_allowed", "Critical terminal approval is disabled.")

class TerminalApprovalAuthority:
    def __init__(self, signing_key: bytes, policy: TerminalApprovalPolicy | None = None):
        if not isinstance(signing_key, (bytes, bytearray)) or len(signing_key) < 32:
            raise TerminalApprovalValidationError("invalid_signing_key", "Signing key must be at least 32 bytes.")
        self._key = bytes(signing_key)
        self.policy = policy or TerminalApprovalPolicy()
        if self.policy.default_ttl_seconds < 1 or self.policy.maximum_ttl_seconds < self.policy.default_ttl_seconds:
            raise TerminalApprovalValidationError("invalid_policy", "Approval TTL policy is invalid.")
        if min(
            self.policy.max_active_tokens,
            self.policy.max_revoked_tokens,
            self.policy.max_consumed_tokens,
            self.policy.max_decisions,
        ) < 1:
            raise TerminalApprovalValidationError("invalid_policy", "Approval registry limits must be positive.")
        self._lock = threading.RLock()
        self._active: dict[str, TerminalApprovalClaims] = {}
        self._revoked: dict[str, int] = {}
        self._consumed: dict[str, int] = {}
        self._decisions: list[TerminalApprovalDecision] = []

    def _record(self, decision: TerminalApprovalDecision) -> TerminalApprovalDecision:
        with self._lock:
            self._decisions.append(decision)
            if len(self._decisions) > self.policy.max_decisions:
                del self._decisions[: len(self._decisions) - self.policy.max_decisions]
        return decision

    def _prune_map(self, value: dict[str, int], maximum: int) -> None:
        if len(value) <= maximum:
            return
        for key, _ in sorted(value.items(), key=lambda item: (item[1], item[0]))[: len(value) - maximum]:
            value.pop(key, None)

    def issue(self, request: TerminalApprovalRequest) -> TerminalApprovalToken:
        subject = _validate_text("subject", request.subject)
        role = _validate_text("role", request.role, maximum=32).lower()
        project_id = _validate_text("project_id", request.project_id)
        plan_sha256 = _validate_hash("plan_sha256", request.plan_sha256)
        command_id = _validate_text("command_id", request.command_id)
        session_id = _validate_text("session_id", request.session_id)
        risk = _validate_text("risk", request.risk, maximum=16).lower()
        if risk not in _ALLOWED_RISKS:
            raise TerminalApprovalValidationError("invalid_risk", "Unknown terminal risk.")
        _authorize_role(self.policy, role, risk)

        issued_at = int(request.requested_at)
        expires_at = int(request.expires_at) if request.expires_at is not None else issued_at + self.policy.default_ttl_seconds
        ttl = expires_at - issued_at
        if ttl < 1 or ttl > self.policy.maximum_ttl_seconds:
            raise TerminalApprovalValidationError("invalid_expiry", "Approval expiry is outside policy bounds.")

        token_id = secrets.token_hex(16)
        claims = TerminalApprovalClaims(
            token_id=token_id,
            issuer=self.policy.issuer,
            audience=self.policy.audience,
            subject=subject,
            role=role,
            project_id=project_id,
            plan_sha256=plan_sha256,
            command_id=command_id,
            session_id=session_id,
            risk=risk,
            issued_at=issued_at,
            not_before=issued_at,
            expires_at=expires_at,
            one_time_use=self.policy.require_one_time_use,
            approval_reason=str(request.approval_reason)[:512],
            metadata=_sanitize_metadata(request.metadata),
        )
        payload = _canonical_json(asdict(claims)).encode("utf-8")
        encoded = _b64e(payload)
        signature = _b64e(hmac.new(self._key, encoded.encode("ascii"), hashlib.sha256).digest())
        token = f"v1.{encoded}.{signature}"

        with self._lock:
            if len(self._active) >= self.policy.max_active_tokens:
                raise TerminalApprovalValidationError("approval_capacity_reached", "Active approval capacity reached.")
            self._active[token_id] = claims

        return TerminalApprovalToken(
            token=token,
            token_id=token_id,
            expires_at=expires_at,
            claims_sha256=terminal_approval_claims_sha256(claims),
        )

    def _decode(self, token: str) -> TerminalApprovalClaims:
        parts = str(token).split(".")
        if len(parts) != 3 or parts[0] != "v1":
            raise TerminalApprovalValidationError("invalid_token", "Approval token format is invalid.")
        encoded, supplied = parts[1], parts[2]
        expected = _b64e(hmac.new(self._key, encoded.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(supplied, expected):
            raise TerminalApprovalValidationError("invalid_signature", "Approval token signature is invalid.")
        try:
            data = json.loads(_b64d(encoded).decode("utf-8"))
            return TerminalApprovalClaims(**data)
        except (ValueError, TypeError, UnicodeDecodeError) as exc:
            raise TerminalApprovalValidationError("invalid_token", "Approval token payload is invalid.") from exc

    def verify(
        self,
        token: str,
        context: TerminalApprovalContext,
        *,
        consume: bool = True,
    ) -> TerminalApprovalDecision:
        try:
            claims = self._decode(token)
            claims_hash = terminal_approval_claims_sha256(claims)
            now = int(context.now)

            if claims.issuer != self.policy.issuer or claims.audience != self.policy.audience:
                return self._record(_decision(False, "invalid", "issuer_or_audience_mismatch", "Approval token issuer or audience is invalid.", token_id=claims.token_id, claims_sha256=claims_hash))
            with self._lock:
                if claims.token_id in self._revoked:
                    return self._record(_decision(False, "revoked", "approval_revoked", "Approval token has been revoked.", token_id=claims.token_id, claims_sha256=claims_hash))
                if claims.token_id in self._consumed:
                    return self._record(_decision(False, "consumed", "approval_replayed", "Approval token has already been consumed.", token_id=claims.token_id, claims_sha256=claims_hash))
                registered = self._active.get(claims.token_id)
            if registered is None or terminal_approval_claims_sha256(registered) != claims_hash:
                return self._record(_decision(False, "invalid", "approval_not_registered", "Approval token is not active.", token_id=claims.token_id, claims_sha256=claims_hash))
            if now + self.policy.clock_skew_seconds < claims.not_before:
                return self._record(_decision(False, "invalid", "approval_not_yet_valid", "Approval token is not yet valid.", token_id=claims.token_id, claims_sha256=claims_hash))
            if now - self.policy.clock_skew_seconds >= claims.expires_at:
                with self._lock:
                    self._active.pop(claims.token_id, None)
                return self._record(_decision(False, "expired", "approval_expired", "Approval token has expired.", token_id=claims.token_id, claims_sha256=claims_hash))

            comparisons = (
                ("subject", claims.subject, context.subject),
                ("role", claims.role, context.role),
                ("risk", claims.risk, context.risk),
            )
            if self.policy.require_project_binding:
                comparisons += (("project_id", claims.project_id, context.project_id),)
            if self.policy.require_command_binding:
                comparisons += (
                    ("plan_sha256", claims.plan_sha256, context.plan_sha256),
                    ("command_id", claims.command_id, context.command_id),
                )
            if self.policy.require_session_binding:
                comparisons += (("session_id", claims.session_id, context.session_id),)

            for name, expected, actual in comparisons:
                if str(expected) != str(actual):
                    return self._record(_decision(False, "denied", f"{name}_mismatch", f"Approval token {name} binding does not match.", token_id=claims.token_id, claims_sha256=claims_hash))

            _authorize_role(self.policy, context.role, context.risk)

            consumed = False
            if consume and claims.one_time_use:
                with self._lock:
                    if claims.token_id in self._consumed:
                        return self._record(_decision(False, "consumed", "approval_replayed", "Approval token has already been consumed.", token_id=claims.token_id, claims_sha256=claims_hash))
                    self._active.pop(claims.token_id, None)
                    self._consumed[claims.token_id] = now
                    self._prune_map(self._consumed, self.policy.max_consumed_tokens)
                    consumed = True

            return self._record(_decision(True, "approved", "approval_valid", "Approval token is valid.", token_id=claims.token_id, claims_sha256=claims_hash, consumed=consumed))
        except TerminalApprovalValidationError as exc:
            return self._record(_decision(False, "invalid", exc.code, exc.message))

    def revoke(self, token_id: str, *, revoked_at: int, reason: str = "") -> TerminalApprovalDecision:
        token_id = _validate_text("token_id", token_id, maximum=64)
        with self._lock:
            if token_id in self._consumed:
                return self._record(_decision(False, "consumed", "approval_already_consumed", "Consumed approvals cannot be revoked.", token_id=token_id))
            existed = token_id in self._active
            self._active.pop(token_id, None)
            self._revoked[token_id] = int(revoked_at)
            self._prune_map(self._revoked, self.policy.max_revoked_tokens)
        return self._record(_decision(existed, "revoked", "approval_revoked" if existed else "approval_not_found", "Approval token revoked." if existed else "Approval token was not active.", token_id=token_id, metadata={"reason": str(reason)[:512]}))

    def list_decisions(self, *, token_id: str | None = None, limit: int = 100) -> list[TerminalApprovalDecision]:
        if limit < 1:
            return []
        with self._lock:
            values = list(self._decisions)
        if token_id:
            values = [item for item in values if item.token_id == token_id]
        return values[-min(limit, self.policy.max_decisions):]

    def active_token_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._active)

    def revoked_token_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._revoked)

    def consumed_token_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._consumed)

def build_terminal_approval_authority(
    signing_key: bytes,
    policy: TerminalApprovalPolicy | None = None,
) -> TerminalApprovalAuthority:
    return TerminalApprovalAuthority(signing_key, policy)

def terminal_approval_policy_json(policy: TerminalApprovalPolicy) -> str:
    return _canonical_json(asdict(policy))
