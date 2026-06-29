from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import (
    CONTRACT_VERSION,
    DISABLED_CAPABILITIES,
    PHASE_26A,
    SAFETY_FLAGS,
    SERVICE_NAME,
    disabled_capability_report,
    validation_error,
)

router = APIRouter(prefix="/api", tags=["Phase 26A contract"])

MAX_CHAT_MESSAGE_LENGTH = 8000
BLOCKED_PAYLOAD_FIELDS = {
    "file",
    "files",
    "upload",
    "uploads",
    "image",
    "images",
    "photo",
    "photos",
    "audio",
    "voice",
    "blob",
    "bytes",
}


@router.get("/health")
def phase26a_health():
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "phase": PHASE_26A,
        "status": "healthy",
        "mode": "contract-only",
        **disabled_capability_report(),
    }


@router.get("/contract")
def phase26a_contract_manifest():
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "phase": PHASE_26A,
        "contractVersion": CONTRACT_VERSION,
        "enabledEndpoints": [
            "GET /api/health",
            "GET /api/contract",
            "POST /api/chat",
        ],
        "disabledCapabilities": DISABLED_CAPABILITIES,
        "approvalGate": {
            "requiredBeforeProductPlan": True,
            "requiredBeforePreview": True,
            "requiredBeforeCodeGeneration": True,
        },
    }


@router.post("/chat")
async def phase26a_chat_contract(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content=validation_error("request body must be valid JSON"))

    if not isinstance(payload, dict):
        return JSONResponse(status_code=400, content=validation_error("request body must be a JSON object"))

    blocked_fields = sorted(BLOCKED_PAYLOAD_FIELDS.intersection(payload.keys()))
    if blocked_fields:
        return JSONResponse(
            status_code=400,
            content=validation_error(
                "file, image, audio, and upload payloads are disabled in Phase 26A"
            ),
        )

    if "message" not in payload:
        return JSONResponse(status_code=400, content=validation_error("message is required"))

    message = payload.get("message")
    if not isinstance(message, str):
        return JSONResponse(status_code=400, content=validation_error("message must be a string"))

    if not message.strip():
        return JSONResponse(status_code=400, content=validation_error("message is required"))

    if len(message) > MAX_CHAT_MESSAGE_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"message must be {MAX_CHAT_MESSAGE_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"local-session-{uuid4().hex[:12]}"

    return {
        "ok": True,
        "phase": PHASE_26A,
        "mode": "contract-only",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": (
                "IdeasForgeAI backend contract is active. Real AI generation is not connected yet. "
                "Phase 26B will add backend-only OpenAI integration after approval."
            ),
        },
        "next": {
            "canGenerateProductPlan": False,
            "canGeneratePreview": False,
            "canGenerateCode": False,
            "approvalRequired": True,
        },
        "safety": SAFETY_FLAGS,
    }
