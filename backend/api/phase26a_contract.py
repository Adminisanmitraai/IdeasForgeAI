from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import (
    CONTRACT_VERSION,
    DISABLED_CAPABILITIES,
    PHASE_27A,
    SERVICE_NAME,
    disabled_capability_report,
    is_openai_configured,
    safety_flags,
    validation_error,
)

router = APIRouter(prefix="/api", tags=["Phase 26B backend chat"])

MAX_CHAT_MESSAGE_LENGTH = 8000
OPENAI_TIMEOUT_SECONDS = 30
OPENAI_MODEL = "gpt-4.1-mini"
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

IDEASFORGEAI_SYSTEM_INSTRUCTION = (
    "You are IdeasForgeAI's backend-only product chat assistant. Be professional. "
    "Help users turn ideas into polished app, website, and product concepts. "
    "Do not claim code generation is active yet. Do not claim preview generation is active yet. "
    "Ask concise follow-up questions only when needed. Make outputs production-ready, detailed, "
    "and more polished than Lovable-level output."
)


@router.get("/health")
def phase26a_health():
    return {
        "ok": True,
        "service": SERVICE_NAME,
        "phase": PHASE_27A,
        "status": "healthy",
        "mode": "backend-openai-chat" if is_openai_configured() else "backend-chat-not-configured",
        **disabled_capability_report(),
    }


@router.get("/contract")
def phase26a_contract_manifest():
    openai_enabled = is_openai_configured()
    enabled_capabilities = ["openai_chat", "sector_classification", "product_generation", "preview_generation", "approval_gate"] if openai_enabled else []
    disabled_capabilities = list(DISABLED_CAPABILITIES)
    if not openai_enabled:
        disabled_capabilities.insert(0, "openai_chat")
        disabled_capabilities.insert(1, "product_generation")
        disabled_capabilities.insert(2, "preview_generation")

    return {
        "ok": True,
        "service": SERVICE_NAME,
        "phase": PHASE_27A,
        "contractVersion": CONTRACT_VERSION,
        "enabledEndpoints": [
            "GET /api/health",
            "GET /api/contract",
            "POST /api/chat",
            "POST /api/sector-classifier",
            "POST /api/product-plan",
            "POST /api/preview-plan",
            "POST /api/approval-gate",
            "GET /api/approval-gate/status",
        ],
        "enabledCapabilities": enabled_capabilities,
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

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"local-session-{uuid4().hex[:12]}"

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27A,
                "mode": "backend-chat-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": (
                        "Backend chat is ready, but OpenAI is not configured for this environment yet. "
                        "Set OPENAI_API_KEY on the backend service to enable real chat responses."
                    ),
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment.",
                },
                "next": {
                    "canGenerateProductPlan": True,
                    "canGeneratePreview": True,
                    "canGenerateCode": False,
                    "approvalRequired": True,
                },
                "safety": safety_flags(),
            },
        )

    try:
        try:
            import truststore

            truststore.inject_into_ssl()
        except ImportError:
            pass

        from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, OpenAIError, RateLimitError

        client = OpenAI(timeout=OPENAI_TIMEOUT_SECONDS)
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=IDEASFORGEAI_SYSTEM_INSTRUCTION,
            input=message.strip(),
        )
        assistant_content = response.output_text.strip()
    except ImportError:
        return JSONResponse(
            status_code=500,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_DEPENDENCY_MISSING",
                message="The OpenAI SDK is not installed in this backend environment.",
            ),
        )
    except AuthenticationError:
        return JSONResponse(
            status_code=401,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_AUTH_ERROR",
                message="OpenAI authentication failed. Check the backend OPENAI_API_KEY setting.",
            ),
        )
    except RateLimitError:
        return JSONResponse(
            status_code=429,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_RATE_LIMIT",
                message="OpenAI rate limit was reached. Try again shortly.",
            ),
        )
    except APITimeoutError:
        return JSONResponse(
            status_code=504,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_TIMEOUT",
                message="OpenAI request timed out. Try again shortly.",
            ),
        )
    except APIConnectionError:
        return JSONResponse(
            status_code=503,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_CONNECTION_ERROR",
                message="OpenAI could not be reached from the backend. Try again shortly.",
            ),
        )
    except OpenAIError:
        return JSONResponse(
            status_code=502,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_ERROR",
                message="OpenAI returned an error. Try again shortly.",
            ),
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content=_openai_error_response(
                session_id=session_id,
                code="OPENAI_GENERAL_FAILURE",
                message="Backend chat failed safely. Try again shortly.",
            ),
        )

    return {
        "ok": True,
        "phase": PHASE_27A,
        "mode": "backend-openai-chat",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": assistant_content,
        },
        "next": {
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "approvalRequired": True,
        },
        "safety": safety_flags(),
    }


def _openai_error_response(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27A,
        "mode": "backend-openai-chat",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "next": {
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "approvalRequired": True,
        },
        "safety": safety_flags(),
    }
