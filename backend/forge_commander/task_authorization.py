from __future__ import annotations

import hmac, json, time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from hashlib import sha256
from pathlib import Path

TASK_AUTH_VERSION = "forge-commander.task-authorization.v1"

def _b64(data: bytes) -> str:
    return urlsafe_b64encode(data).decode("ascii").rstrip("=")

def _unb64(value: str) -> bytes:
    return urlsafe_b64decode(value + "=" * (-len(value) % 4))

def issue_task_authorization(claims: dict, *, signing_key: str) -> str:
    if not signing_key:
        raise ValueError("task_authorization_signing_unavailable")
    required={"authorization_id","task_id","owner_subject","device_id","environment",
              "project_root","applications","allowed_actions","issued_at","expires_at"}
    if set(claims) != required:
        raise ValueError("task_authorization_claims_invalid")
    if claims["environment"] == "production":
        raise PermissionError("autonomous_production_authorization_denied")
    body=json.dumps(claims,sort_keys=True,separators=(",",":")).encode()
    sig=hmac.new(signing_key.encode(),body,sha256).digest()
    return _b64(body)+"."+_b64(sig)

def validate_task_authorization(token: str, *, signing_key: str, owner_subject: str,
                                device_id: str, action: str, artifact_path: str|None=None) -> dict:
    try:
        body64,sig64=token.split(".",1); body=_unb64(body64); supplied=_unb64(sig64)
    except Exception as exc:
        raise PermissionError("task_authorization_malformed") from exc
    expected=hmac.new(signing_key.encode(),body,sha256).digest()
    if not hmac.compare_digest(supplied,expected):
        raise PermissionError("task_authorization_signature_invalid")
    claims=json.loads(body)
    if claims.get("owner_subject") != owner_subject or claims.get("device_id") != device_id:
        raise PermissionError("task_authorization_principal_mismatch")
    if claims.get("environment") == "production":
        raise PermissionError("autonomous_production_authorization_denied")
    if int(claims.get("expires_at",0)) <= int(time.time()):
        raise PermissionError("task_authorization_expired")
    if action not in set(claims.get("allowed_actions") or ()):
        raise PermissionError("action_outside_task_authorization")
    if artifact_path:
        root=Path(str(claims.get("project_root") or "")).resolve()
        artifact=Path(artifact_path).resolve()
        if artifact != root and root not in artifact.parents:
            raise PermissionError("artifact_outside_authorized_project")
    return claims
# R7 governed live patch certification
