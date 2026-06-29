from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import (
    CONTRACT_VERSION,
    DISABLED_CAPABILITIES,
    PHASE_27E,
    SERVICE_NAME,
    disabled_capability_report,
    safety_flags,
    validation_error,
)

router = APIRouter(prefix="/api", tags=["Phase 26B backend chat"])

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

DISCOVERY_STEPS = ("idea", "users", "features", "style", "summary")
SESSION_STATE: dict[str, dict] = {}


@router.get("/health")
def phase26a_health():
    return {
        "ok": True,
        "service": "IdeasForgeAI backend",
        "status": "ready",
    }


@router.get("/contract")
def phase26a_contract_manifest():
    disabled_capabilities = list(DISABLED_CAPABILITIES)
    disabled_capabilities.insert(0, "external_ai_provider_calls")
    disabled_capabilities.insert(1, "product_generation")
    disabled_capabilities.insert(2, "preview_generation")

    return {
        "ok": True,
        "service": SERVICE_NAME,
        "phase": PHASE_27E,
        "contractVersion": CONTRACT_VERSION,
        "enabledEndpoints": [
            "GET /api/health",
            "GET /api/contract",
            "POST /api/chat",
            "POST /api/sector-classifier",
            "POST /api/requirements",
            "POST /api/workflow-map",
            "POST /api/output-type",
            "POST /api/product-flow",
            "POST /api/product-plan",
            "POST /api/preview-plan",
            "POST /api/approval-gate",
            "GET /api/approval-gate/status",
        ],
        "enabledCapabilities": ["studio_v4_local_discovery_chat"],
        "disabledCapabilities": disabled_capabilities,
        "approvalGate": {
            "requiredBeforeProductPlan": False,
            "requiredBeforePreview": False,
            "requiredBeforeCodeGeneration": True,
        },
        "safety": safety_flags(),
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

    session_id = payload.get("session_id") or payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"studio-v4-{uuid4().hex[:12]}"

    session = SESSION_STATE.setdefault(
        session_id,
        {
            "step_index": 0,
            "answers": {},
        },
    )

    assistant_content = _next_discovery_reply(session, message.strip())
    stage = "planning" if session["step_index"] >= 4 else "discovery"

    return {
        "ok": True,
        "session_id": session_id,
        "reply": assistant_content,
        "stage": stage,
        "suggestions": _suggestions_for_step(session["step_index"]),
        "preview_allowed": False,
        "generation_allowed": False,
    }


def _next_discovery_reply(session: dict, message: str) -> str:
    step_index = session.get("step_index", 0)
    step = DISCOVERY_STEPS[min(step_index, len(DISCOVERY_STEPS) - 1)]
    session["answers"][step] = message

    if step == "idea":
        session["step_index"] = 1
        return (
            "Great. Who are the primary users for this product, and what job should it help them finish first?"
        )

    if step == "users":
        session["step_index"] = 2
        return "What are the 3 core features this product must include in the first version?"

    if step == "features":
        session["step_index"] = 3
        return "What visual style should the product have: clean SaaS, premium agency, dashboard-heavy, or something else?"

    if step == "style":
        session["step_index"] = 4
        answers = session["answers"]
        return (
            "Here is the locked discovery summary so far: "
            f"product idea: {answers.get('idea', 'not specified')}; "
            f"target users: {answers.get('users', 'not specified')}; "
            f"core features: {answers.get('features', 'not specified')}; "
            f"preferred style: {answers.get('style', 'not specified')}. "
            "Preview and generation remain locked. What should we refine before planning the preview?"
        )

    session["step_index"] = 4
    return (
        "Got it. I can keep refining the product plan safely, but preview and app generation remain locked for now. "
        "Which part should we refine next: users, features, workflow, or visual style?"
    )


def _suggestions_for_step(step_index: int) -> list[str]:
    suggestions_by_step = {
        1: ["Small business owners", "Internal sales team"],
        2: ["Lead tracking", "Follow-up reminders"],
        3: ["Clean SaaS", "Premium dashboard"],
        4: ["Refine users", "Refine features"],
    }
    return suggestions_by_step.get(step_index, ["Clarify workflow", "Refine product scope"])
