import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 26E preview generator"])

PHASE_26E = "26E"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_PREVIEW_INPUT_LENGTH = 20000

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

PREVIEW_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Preview Generator Agent.

Your job is to convert an approved product plan or user idea into a safe, professional preview specification.

IdeasForgeAI is a universal AI builder for work, business, study, content creation, and daily life.

The preview must be:
- mobile-first
- professional
- polished
- practical
- production-useful
- better than generic app builder output
- suitable for app, website, dashboard, report, presentation, catalog, proposal, content pack, or workflow assistant

Important rules:
- Do not generate code.
- Do not generate HTML.
- Do not generate CSS.
- Do not generate JavaScript.
- Do not write files.
- Do not claim code generation is active.
- Do not claim export generation is active.
- Keep code generation approval-gated.
- Keep database/auth/upload/OCR/voice disabled.
- Return JSON only. No markdown. No code fences.

Return a preview specification with:
previewName, sector, outputType, designDirection, mobileExperience, desktopExperience,
screens, sections, components, interactionFlow, emptyStates, loadingStates,
responsiveRules, accessibilityNotes, contentTone, visualPolishNotes,
approvalGates, notIncludedYet, betterThanLovableQualityNotes.
"""


def _phase26e_safety() -> dict:
    flags = safety_flags()
    flags["productGenerationEnabled"] = True
    flags["previewGenerationEnabled"] = True
    flags["codeGenerationEnabled"] = False
    return flags


def _safe_text(value, fallback=""):
    if isinstance(value, str):
        return value.strip()
    return fallback


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    return text


def _fallback_preview(idea: str, product_plan: dict, sector: str, output_type: str) -> dict:
    plan_name = ""
    if isinstance(product_plan, dict):
        plan_name = product_plan.get("productName", "")

    return {
        "previewName": plan_name or "IdeasForgeAI Professional Preview",
        "sector": sector or product_plan.get("sector", "general professional workflow") if isinstance(product_plan, dict) else sector or "general professional workflow",
        "outputType": output_type or product_plan.get("outputType", "AI assistant app preview") if isinstance(product_plan, dict) else output_type or "AI assistant app preview",
        "designDirection": {
            "style": "premium, clean, mobile-first, professional",
            "layout": "chat intake on top, workflow dashboard in center, approval controls at bottom",
            "tone": "clear, useful, business-ready"
        },
        "mobileExperience": [
            "Simple chat-style idea intake",
            "Compact product summary card",
            "Step-by-step workflow preview",
            "Clear approval gate before code or export"
        ],
        "desktopExperience": [
            "Left AI workspace panel",
            "Main preview canvas",
            "Right-side plan/quality checklist",
            "Approval and revision controls"
        ],
        "screens": [
            "Welcome / idea intake screen",
            "Generated product plan screen",
            "Workflow preview screen",
            "Output format preview screen",
            "Approval gate screen"
        ],
        "sections": [
            "Hero summary",
            "Problem solved",
            "Target users",
            "Core workflow",
            "Inputs and outputs",
            "Safety and approval gates"
        ],
        "components": [
            "Assistant chat bubble",
            "Product summary card",
            "Workflow step cards",
            "Data input chips",
            "Output/export badges",
            "Approval gate banner"
        ],
        "interactionFlow": [
            "User submits idea",
            "System creates product plan",
            "System creates preview specification",
            "User reviews preview",
            "Preview/code/export remain gated until later approval"
        ],
        "emptyStates": [
            "No idea entered yet",
            "Waiting for product plan",
            "Preview not approved yet"
        ],
        "loadingStates": [
            "Generating preview structure",
            "Polishing layout direction",
            "Preparing approval checklist"
        ],
        "responsiveRules": [
            "Mobile layout uses single-column cards",
            "Desktop layout uses builder workspace and preview canvas",
            "Large buttons and readable text for non-technical users"
        ],
        "accessibilityNotes": [
            "High contrast text",
            "Large tap targets",
            "Clear status labels",
            "No hidden critical actions"
        ],
        "contentTone": "professional, simple, helpful, non-technical",
        "visualPolishNotes": [
            "Use clean spacing",
            "Use premium card shadows",
            "Use consistent typography",
            "Avoid clutter",
            "Show clear next actions"
        ],
        "approvalGates": {
            "beforePreviewGeneration": False,
            "beforeCodeGeneration": True,
            "beforeExport": True,
            "beforeDeployment": True
        },
        "notIncludedYet": [
            "Code generation",
            "Real file export",
            "Database",
            "Authentication",
            "Upload processing",
            "OCR/image/voice processing"
        ],
        "betterThanLovableQualityNotes": [
            "Sector-aware preview",
            "Professional workflow mapping",
            "Mobile-first screen planning",
            "Approval-gated production safety",
            "Business-ready presentation"
        ]
    }


@router.post("/preview-plan")
async def generate_preview_plan(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 26E"),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"preview-plan-{uuid4().hex[:12]}"

    idea = _safe_text(payload.get("idea"))
    sector = _safe_text(payload.get("sector"))
    output_type = _safe_text(payload.get("outputType"))
    product_plan = payload.get("productPlan") or payload.get("plan")

    if product_plan is None and not idea:
        return JSONResponse(status_code=400, content=validation_error("productPlan or idea is required"))

    input_size = len(idea) + len(json.dumps(product_plan, ensure_ascii=False, default=str))
    if input_size > MAX_PREVIEW_INPUT_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"preview input must be {MAX_PREVIEW_INPUT_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_26E,
                "mode": "preview-generator-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Preview Generator is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase26e_safety(),
            },
        )

    prompt = {
        "task": "Create a safe preview specification for IdeasForgeAI. Do not generate code.",
        "idea": idea,
        "sector": sector or "infer from idea/product plan",
        "outputType": output_type or "infer best output type",
        "productPlan": product_plan or {},
    }

    try:
        try:
            import truststore
            truststore.inject_into_ssl()
        except ImportError:
            pass

        from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, OpenAIError, RateLimitError

        client = OpenAI(timeout=OPENAI_TIMEOUT_SECONDS)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            instructions=PREVIEW_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False, default=str),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            preview = json.loads(output_text)
        except Exception:
            preview = _fallback_preview(idea, product_plan if isinstance(product_plan, dict) else {}, sector, output_type)
            preview["rawAIPreview"] = output_text

    except AuthenticationError:
        return JSONResponse(status_code=401, content=_agent_error(session_id, "OPENAI_AUTH_ERROR", "OpenAI authentication failed. Check backend OPENAI_API_KEY."))
    except RateLimitError:
        return JSONResponse(status_code=429, content=_agent_error(session_id, "OPENAI_RATE_LIMIT", "OpenAI rate limit reached. Try again shortly."))
    except APITimeoutError:
        return JSONResponse(status_code=504, content=_agent_error(session_id, "OPENAI_TIMEOUT", "OpenAI request timed out. Try again shortly."))
    except APIConnectionError:
        return JSONResponse(status_code=503, content=_agent_error(session_id, "OPENAI_CONNECTION_ERROR", "OpenAI could not be reached from the backend."))
    except OpenAIError:
        return JSONResponse(status_code=502, content=_agent_error(session_id, "OPENAI_ERROR", "OpenAI returned an error. Try again shortly."))
    except Exception:
        return JSONResponse(status_code=500, content=_agent_error(session_id, "PREVIEW_PLAN_FAILURE", "Preview plan generation failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_26E,
        "service": SERVICE_NAME,
        "mode": "preview-plan-generator",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Preview specification generated. Code generation, export, and deployment remain approval-gated for later phases."
        },
        "preview": preview,
        "next": {
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase26e_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_26E,
        "mode": "preview-plan-generator",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase26e_safety(),
    }
