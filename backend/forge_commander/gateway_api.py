from __future__ import annotations

from datetime import datetime, timezone
import base64
import binascii
import hmac
import os
import secrets
import tempfile
import time
from hashlib import sha256
from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect

from .cloud_device_registry import DeviceSession
from .cloud_task_channel import DeviceTaskResultEnvelope, build_task_envelope
from .gateway_auth import parse_bearer_principal
from .device_auth import issue_device_token, parse_device_token
from .gateway_session_manager import GatewaySessionManager, LiveGatewaySession

FORGE_COMMANDER_GATEWAY_API_VERSION = "forge-commander.gateway-api.v1"

router = APIRouter(prefix="/forge-commander", tags=["forge-commander"])
session_manager = GatewaySessionManager()
_PAIRING_TICKETS: dict[str, tuple[str, int]] = {}

def _purge_pairing_tickets(now: int) -> None:
    for digest, (_, expires_at) in list(_PAIRING_TICKETS.items()):
        if expires_at <= now:
            _PAIRING_TICKETS.pop(digest, None)

@router.get("/health")
def gateway_health():
    return {"ok": True, "service": "forge-commander-gateway"}

@router.post("/device/pairing-ticket")
def create_pairing_ticket(authorization: str | None = Header(default=None)):
    token = authorization[7:].strip() if (authorization or "").startswith("Bearer ") else ""
    principal = parse_device_token(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    now = int(time.time())
    _purge_pairing_tickets(now)
    code = secrets.token_urlsafe(24)
    digest = sha256(code.encode("utf-8")).hexdigest()
    expires_at = now + 600
    _PAIRING_TICKETS[digest] = (principal.owner_subject, expires_at)
    return {"pairing_code": code, "expires_at": expires_at, "ttl_seconds": 600}

@router.post("/device/pair")
def pair_device(payload: dict):
    code = str(payload.get("pairing_code", "")).strip()
    device_id = str(payload.get("device_id", "")).strip()
    if not code or not device_id:
        raise HTTPException(status_code=400, detail="pairing_code_and_device_id_required")
    now = int(time.time())
    _purge_pairing_tickets(now)
    digest = sha256(code.encode("utf-8")).hexdigest()
    ticket = _PAIRING_TICKETS.pop(digest, None)
    if ticket is None:
        raise HTTPException(status_code=401, detail="invalid_or_expired_pairing_code")
    owner_subject, expires_at = ticket
    if expires_at <= now:
        raise HTTPException(status_code=401, detail="invalid_or_expired_pairing_code")
    signing_key = os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "")
    if not signing_key:
        raise HTTPException(status_code=503, detail="gateway_signing_unavailable")
    device_expires_at = now + 90 * 24 * 60 * 60
    token = issue_device_token(owner_subject, device_id, signing_key=signing_key, expires_at=device_expires_at)
    return {
        "enrolled": True,
        "owner_subject": owner_subject,
        "device_id": device_id,
        "device_token": token,
        "expires_at": device_expires_at,
    }

@router.get("/device/peers")
def device_peers(authorization: str | None = Header(default=None)):
    token = authorization[7:].strip() if (authorization or "").startswith("Bearer ") else ""
    principal = parse_device_token(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    peers = [
        {
            "device_id": live.session.device_id,
            "session_id": live.session.session_id,
            "online": True,
            "last_heartbeat_at": live.last_heartbeat_at,
        }
        for live in session_manager.live_sessions(owner_subject=principal.owner_subject)
    ]
    return {
        "owner_subject": principal.owner_subject,
        "requesting_device_id": principal.device_id,
        "devices": peers,
    }

@router.get("/device/peers/{device_id}/hardware")
async def device_peer_hardware(device_id: str, authorization: str | None = Header(default=None)):
    token = authorization[7:].strip() if (authorization or "").startswith("Bearer ") else ""
    principal = parse_device_token(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    live = session_manager.get(device_id)
    if live is None or live.session.owner_subject != principal.owner_subject:
        raise HTTPException(status_code=404, detail="peer_not_found")
    task = build_task_envelope(
        live.session,
        instruction="Read training-worker hardware capability.",
        required_capability="device.hardware",
        approval_required=False,
        request={"capability": "device.hardware"},
        approval_granted=False,
    )
    await session_manager.dispatch(task)
    result = await session_manager.wait_result(task.task_id, timeout_seconds=10.0)
    if result is None:
        raise HTTPException(status_code=504, detail="peer_hardware_timeout")
    if not result.succeeded:
        raise HTTPException(status_code=502, detail=result.reason or "peer_hardware_failed")
    output = result.output if isinstance(result.output, dict) else {}
    return {
        "device_id": device_id,
        "online": True,
        "hardware": output.get("data", {}),
    }


def _device_principal_from_header(authorization: str | None):
    token = authorization[7:].strip() if (authorization or "").startswith("Bearer ") else ""
    principal = parse_device_token(token)
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    return principal


_VOICE_AUDIO_MIME_SUFFIX = {
    "audio/webm": ".webm",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/ogg": ".ogg",
}
_MAX_VOICE_AUDIO_BYTES = 8 * 1024 * 1024


@router.post("/device/voice/transcribe")
def device_voice_transcribe(
    payload: dict,
    authorization: str | None = Header(default=None),
):
    principal = _device_principal_from_header(authorization)
    encoded = str(payload.get("audio_base64", "")).strip()
    mime_type = str(payload.get("mime_type", "audio/webm")).strip().lower()
    language_hint = str(payload.get("language_hint", "en")).strip().lower()

    if not encoded:
        raise HTTPException(status_code=400, detail="audio_base64_required")
    suffix = _VOICE_AUDIO_MIME_SUFFIX.get(mime_type)
    if suffix is None:
        raise HTTPException(status_code=400, detail="unsupported_audio_mime")
    if len(encoded) > (_MAX_VOICE_AUDIO_BYTES * 2):
        raise HTTPException(status_code=413, detail="audio_payload_too_large")

    try:
        audio_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="audio_base64_invalid")
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio_empty")
    if len(audio_bytes) > _MAX_VOICE_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="audio_payload_too_large")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise HTTPException(status_code=503, detail="transcription_provider_unavailable")

    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(audio_bytes)
            temp_path = handle.name

        from openai import (
            APIConnectionError,
            APITimeoutError,
            AuthenticationError,
            OpenAI,
            OpenAIError,
            RateLimitError,
        )

        client = OpenAI(timeout=45)
        with open(temp_path, "rb") as audio_file:
            kwargs = {
                "model": os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe"),
                "file": audio_file,
            }
            if language_hint in {"en", "hi", "bn"}:
                kwargs["language"] = language_hint
            result = client.audio.transcriptions.create(**kwargs)

        text = str(getattr(result, "text", "") or "").strip()
        if not text:
            raise HTTPException(status_code=422, detail="transcription_empty")
        return {
            "ok": True,
            "text": text,
            "provider": "openai",
            "model": os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe"),
            "language_hint": language_hint,
            "device_id": principal.device_id,
            "audio_persisted": False,
        }
    except AuthenticationError:
        raise HTTPException(status_code=502, detail="transcription_auth_failed")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="transcription_rate_limited")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="transcription_timeout")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="transcription_connection_failed")
    except OpenAIError:
        raise HTTPException(status_code=502, detail="transcription_provider_failed")
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


async def _dispatch_peer_training(
    device_id: str,
    *,
    principal,
    capability: str,
    request: dict,
    approval_required: bool,
    approval_granted: bool,
    timeout_seconds: float = 15.0,
):
    live = session_manager.get(device_id)
    if live is None or live.session.owner_subject != principal.owner_subject:
        raise HTTPException(status_code=404, detail="peer_not_found")
    task = build_task_envelope(
        live.session,
        instruction=f"ForgeWa training task: {capability}",
        required_capability=capability,
        approval_required=approval_required,
        request=request,
        approval_granted=approval_granted,
    )
    await session_manager.dispatch(task)
    result = await session_manager.wait_result(task.task_id, timeout_seconds=timeout_seconds)
    if result is None:
        raise HTTPException(status_code=504, detail=f"{capability}_timeout")
    output = result.output if isinstance(result.output, dict) else {}
    if not result.succeeded:
        return {
            "device_id": device_id,
            "succeeded": False,
            "reason": result.reason or f"{capability}_failed",
            "output": output,
        }
    return {
        "device_id": device_id,
        "succeeded": True,
        "reason": result.reason,
        "output": output,
    }


@router.get("/device/peers/{device_id}/training/environment")
async def device_peer_training_environment(
    device_id: str,
    authorization: str | None = Header(default=None),
):
    principal = _device_principal_from_header(authorization)
    return await _dispatch_peer_training(
        device_id,
        principal=principal,
        capability="training.environment",
        request={"job_kind": "cuda_smoke"},
        approval_required=False,
        approval_granted=False,
    )


@router.get("/device/peers/{device_id}/training/status")
async def device_peer_training_status(
    device_id: str,
    authorization: str | None = Header(default=None),
):
    principal = _device_principal_from_header(authorization)
    return await _dispatch_peer_training(
        device_id,
        principal=principal,
        capability="training.status",
        request={},
        approval_required=False,
        approval_granted=False,
    )


@router.post("/device/peers/{device_id}/training/start")
async def device_peer_training_start(
    device_id: str,
    payload: dict,
    authorization: str | None = Header(default=None),
):
    principal = _device_principal_from_header(authorization)
    if str(payload.get("confirm", "")) != "START_TRAINING":
        raise HTTPException(status_code=400, detail="explicit_training_confirmation_required")
    job_kind = str(payload.get("job_kind", "cuda_smoke")).strip()
    if job_kind != "cuda_smoke":
        raise HTTPException(status_code=400, detail="unsupported_job_kind")
    steps = max(20, min(int(payload.get("steps", 120)), 500))
    checkpoint_every = max(10, min(int(payload.get("checkpoint_every", 30)), steps))
    request = {
        "job_kind": "cuda_smoke",
        "project_id": str(payload.get("project_id", "brain"))[:64],
        "steps": steps,
        "checkpoint_every": checkpoint_every,
        "min_free_vram_mb": max(1024, min(int(payload.get("min_free_vram_mb", 4096)), 15000)),
    }
    return await _dispatch_peer_training(
        device_id,
        principal=principal,
        capability="training.start",
        request=request,
        approval_required=True,
        approval_granted=True,
        timeout_seconds=20.0,
    )


@router.post("/device/peers/{device_id}/training/cancel")
async def device_peer_training_cancel(
    device_id: str,
    payload: dict,
    authorization: str | None = Header(default=None),
):
    principal = _device_principal_from_header(authorization)
    if str(payload.get("confirm", "")) != "CANCEL_TRAINING":
        raise HTTPException(status_code=400, detail="explicit_cancel_confirmation_required")
    return await _dispatch_peer_training(
        device_id,
        principal=principal,
        capability="training.cancel",
        request={"job_id": str(payload.get("job_id", ""))[:128]},
        approval_required=True,
        approval_granted=True,
        timeout_seconds=15.0,
    )


@router.get("/mcp/tools")
def list_mcp_tools(authorization: str | None = Header(default=None)):
    principal = parse_bearer_principal(authorization or "")
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    return {"owner_subject": principal.owner_subject, "tools": [
        "list_devices", "get_device_status",
        "device_identity", "device_resources", "device_runtime", "device_hardware",
        "device_storage", "device_processes", "device_network", "device_software",
        "device_dev_environment", "file_list", "file_read_text", "terminal_read",
        "run_device_task", "write_file_text", "delete_file", "run_terminal_profile",
    ]}
@router.post("/device/enroll")
def enroll_device(payload: dict, x_forge_enrollment_secret: str | None = Header(default=None)):
    configured_hash = os.getenv("FORGE_COMMANDER_ENROLLMENT_BOOTSTRAP_SHA256", "")
    allowed_hashes = (configured_hash,) if configured_hash else ()
    presented = (x_forge_enrollment_secret or "").strip()
    presented_hash = sha256(presented.encode("utf-8")).hexdigest() if presented else ""

    print(
        "FC_AUTH_R1C_R2",
        "env_present=", bool(configured_hash),
        "env_len=", len(configured_hash),
        "env_suffix=", configured_hash[-6:] if configured_hash else "EMPTY",
        "presented_len=", len(presented),
        "presented_hash_suffix=", presented_hash[-6:] if presented_hash else "EMPTY",
        flush=True,
    )
    if not presented_hash or not any(hmac.compare_digest(presented_hash, candidate) for candidate in allowed_hashes):
        raise HTTPException(status_code=401, detail="invalid_enrollment_secret")
    owner = str(payload.get("owner_subject", "")).strip()
    device_id = str(payload.get("device_id", "")).strip()
    if not owner or not device_id:
        raise HTTPException(status_code=400, detail="owner_subject_and_device_id_required")
    signing_key = os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "")
    if not signing_key:
        raise HTTPException(status_code=503, detail="gateway_signing_unavailable")
    expires_at = int(time.time()) + 90 * 24 * 60 * 60
    token = issue_device_token(owner, device_id, signing_key=signing_key, expires_at=expires_at)
    return {"enrolled": True, "owner_subject": owner, "device_id": device_id,
            "device_token": token, "expires_at": expires_at}

@router.websocket("/device/ws/{device_id}")
async def device_ws(websocket: WebSocket, device_id: str):
    authorization = websocket.headers.get("authorization", "")
    token = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
    principal = parse_device_token(token, expected_device_id=device_id)
    if principal is None:
        await websocket.close(code=4401)
        return
    session_id = websocket.query_params.get("session_id", "").strip()
    instance_id = websocket.query_params.get("instance_id", "").strip()
    if not session_id or not instance_id:
        await websocket.close(code=4400)
        return
    await websocket.accept()
    now = datetime.now(timezone.utc).isoformat()
    session = DeviceSession(
        session_id=session_id, device_id=device_id,
        owner_subject=principal.owner_subject, instance_id=instance_id,
        connected_at=now, heartbeat_at=now,
    )
    try:
        session_manager.attach(LiveGatewaySession(session, websocket, now))
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "heartbeat":
                heartbeat_at = message.get("at", datetime.now(timezone.utc).isoformat())
                session_manager.heartbeat(device_id, session_id, heartbeat_at)
                await websocket.send_json({"type": "heartbeat_ack", "at": heartbeat_at})
            elif message.get("type") == "result":
                session_manager.accept_result(DeviceTaskResultEnvelope(
                    task_id=str(message.get("task_id", "")), device_id=device_id,
                    session_id=session_id, succeeded=bool(message.get("succeeded")),
                    reason=str(message.get("reason", "device_result")), output=message.get("output"),
                ))
    except WebSocketDisconnect:
        session_manager.detach(device_id, session_id)

__all__ = [
    "FORGE_COMMANDER_GATEWAY_API_VERSION", "router", "session_manager",
]
