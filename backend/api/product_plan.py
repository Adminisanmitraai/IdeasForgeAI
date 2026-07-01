import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 26D product plan generator"])

PHASE_26D = "26D"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_IDEA_LENGTH = 12000
MAX_REFERENCE_IMAGE_TEXT_LENGTH = 1200
REFERENCE_IMAGE_KEYS = {"referenceImage", "reference_image", "imageReference", "image_metadata"}

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

PRODUCT_PLAN_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Product Plan Generator Agent.

Your job is to convert a normal user idea into a professional, approval-ready product plan.
IdeasForgeAI is a universal AI builder for work, business, study, content creation, and daily life.

Supported users include:
employees, bankers, accountants, retailers, restaurant owners, farmers, sales teams, creative agencies,
students, researchers, teachers, medical admin teams, logistics teams, real estate workers,
manufacturers, housewives, home business owners, content creators, Instagram/Reels creators,
online sellers, and small business owners.

Supported outputs include:
AI assistant app, website, dashboard, mobile web app, project report, research report, presentation,
catalog, proposal, inventory tool, sales tracker, accounts tool, restaurant assistant, farming assistant,
social media content pack, reel script pack, Instagram post pack, WhatsApp promo pack, PDF/DOCX/PPTX/Excel export plan.

Important safety:
- Do not generate code.
- Do not generate preview HTML.
- Do not claim database/auth/upload/OCR/voice/export is active yet.
- If referenceImage metadata is provided, mark the plan as image-guided and use it only as layout/style guidance.
- Do not claim image pixels were analyzed. Use metadata, user notes, and safe inference only.
- Do not create medical, legal, financial, or credit decisions as final decisions.
- Keep human approval gates.
- Make every result more polished, practical, professional, mobile-ready, and production-useful than a generic app builder result.

Return JSON only. No markdown. No code fences.
"""


def _phase26d_safety() -> dict:
    flags = safety_flags()
    flags["productGenerationEnabled"] = True
    flags["previewGenerationEnabled"] = False
    flags["codeGenerationEnabled"] = False
    return flags


def _safe_text(value, fallback=""):
    if isinstance(value, str):
        return value.strip()
    return fallback


def _normalize_reference_image(payload: dict) -> dict:
    raw = None
    for key in REFERENCE_IMAGE_KEYS:
        if key in payload:
            raw = payload.get(key)
            break

    if not isinstance(raw, dict):
        return {}

    allowed = {
        "name",
        "fileName",
        "type",
        "mimeType",
        "size",
        "sourcePath",
        "path",
        "width",
        "height",
        "layoutHint",
        "visualNotes",
        "source",
    }
    normalized = {}
    for key in allowed:
        value = raw.get(key)
        if isinstance(value, str):
            value = value.strip()[:MAX_REFERENCE_IMAGE_TEXT_LENGTH]
            if value:
                normalized[key] = value
        elif isinstance(value, (int, float)) and value >= 0:
            normalized[key] = value

    if not normalized:
        return {}

    normalized["inputMode"] = "image-guided-metadata-only"
    normalized["binaryUploadReceived"] = False
    normalized["ocrOrVisionPerformed"] = False
    return normalized


def _image_guidance_fields(reference_image: dict) -> dict:
    if not reference_image:
        return {}

    source_label = (
        reference_image.get("name")
        or reference_image.get("fileName")
        or reference_image.get("sourcePath")
        or reference_image.get("path")
        or "reference image metadata"
    )
    return {
        "inputMode": "image-guided",
        "imageGuided": True,
        "referenceImage": reference_image,
        "visualReferenceSummary": (
            f"Use {source_label} as a safe visual guide for layout density, hierarchy, spacing, "
            "navigation placement, and mobile interface feel. This phase does not inspect pixels."
        ),
        "interfaceDesignPriorities": [
            "Mobile-first screen structure inspired by the reference",
            "Clear top navigation and primary action hierarchy",
            "Card, list, and form density selected for app-interface work",
            "Preview must be polished even without full vision automation",
        ],
    }


def _fallback_plan(idea: str, sector: str, output_type: str, reference_image: dict | None = None) -> dict:
    guessed_sector = sector or "general professional workflow"
    guessed_output = output_type or "AI assistant app / workflow tool"

    plan = {
        "productName": "IdeasForgeAI Work Assistant",
        "sector": guessed_sector,
        "outputType": guessed_output,
        "userRole": "Professional user",
        "targetUsers": ["Employees", "Business owners", "Students", "Creators", "Small teams"],
        "problemSolved": idea,
        "coreWorkflow": [
            "User describes the daily work or goal",
            "System collects required inputs",
            "AI structures the workflow",
            "User reviews the generated plan",
            "Preview/code/export stays approval-gated for later phases"
        ],
        "requiredScreens": [
            "Chat intake screen",
            "Workflow summary screen",
            "Input/data mapping screen",
            "Generated plan screen",
            "Approval gate screen"
        ],
        "aiAssistantBehavior": [
            "Understand the user role and sector",
            "Convert rough ideas into structured workflows",
            "Ask concise follow-up questions only when needed",
            "Suggest professional output formats",
            "Keep safety and approval gates visible"
        ],
        "dataInputs": [
            "User idea",
            "Sector",
            "Role",
            "Current manual workflow",
            "Expected output format"
        ],
        "outputsAndExports": [
            "Structured product plan",
            "Workflow checklist",
            "Screen plan",
            "Future PDF/DOCX/PPTX/Excel export plan"
        ],
        "safetyRules": [
            "No code generation in Phase 26D",
            "No preview generation in Phase 26D",
            "No database/auth/upload/OCR/voice processing",
            "Human approval required before preview/code/export"
        ],
        "approvalGates": {
            "beforeProductPlan": False,
            "beforePreview": True,
            "beforeCodeGeneration": True,
            "beforeExport": True
        },
        "futurePhasesNeeded": [
            "Phase 26E preview generator",
            "Phase 26F approval gate",
            "Document/export phases",
            "Sector preset library"
        ],
        "betterThanLovableQualityNotes": [
            "Sector-aware output",
            "Professional workflow mapping",
            "Production-ready planning",
            "Mobile-ready screen structure",
            "Clear safety and approval gates"
        ]
    }
    plan.update(_image_guidance_fields(reference_image or {}))
    if reference_image:
        plan["requiredScreens"] = [
            "Image-guided mobile home screen",
            "Reference-inspired dashboard screen",
            "Primary action flow screen",
            "Detail/form screen",
            "Approval gate screen",
        ]
    return plan


@router.post("/product-plan")
async def generate_product_plan(request: Request):
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
                "raw file, image, audio, and upload payloads are disabled; send referenceImage metadata only"
            ),
        )

    idea = payload.get("idea")
    if not isinstance(idea, str):
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    idea = idea.strip()
    if not idea:
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    if len(idea) > MAX_IDEA_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"idea must be {MAX_IDEA_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"product-plan-{uuid4().hex[:12]}"

    sector = _safe_text(payload.get("sector"))
    output_type = _safe_text(payload.get("outputType"))
    reference_image = _normalize_reference_image(payload)

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_26D,
                "mode": "product-plan-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Product Plan Generator is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase26d_safety(),
            },
        )

    prompt = {
        "task": "Create an approval-ready IdeasForgeAI product plan.",
        "idea": idea,
        "sector": sector or "infer from idea",
        "outputType": output_type or "infer best output type",
        "inputMode": "image-guided" if reference_image else "text-only",
        "referenceImage": reference_image,
        "requiredJsonShape": {
            "productName": "string",
            "sector": "string",
            "outputType": "string",
            "userRole": "string",
            "targetUsers": ["string"],
            "problemSolved": "string",
            "coreWorkflow": ["string"],
            "requiredScreens": ["string"],
            "aiAssistantBehavior": ["string"],
            "dataInputs": ["string"],
            "outputsAndExports": ["string"],
            "safetyRules": ["string"],
            "approvalGates": {
                "beforeProductPlan": False,
                "beforePreview": True,
                "beforeCodeGeneration": True,
                "beforeExport": True
            },
            "futurePhasesNeeded": ["string"],
            "betterThanLovableQualityNotes": ["string"],
            "imageGuided": "boolean when referenceImage is present",
            "visualReferenceSummary": "string when referenceImage is present",
            "interfaceDesignPriorities": ["string when referenceImage is present"]
        }
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
            instructions=PRODUCT_PLAN_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False),
        )

        output_text = response.output_text.strip()

        try:
            plan = json.loads(output_text)
        except Exception:
            plan = _fallback_plan(idea, sector, output_type, reference_image)
            plan["rawAIPlan"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "PRODUCT_PLAN_FAILURE", "Product plan generation failed safely. Try again shortly."))

    if reference_image and isinstance(plan, dict):
        plan.update(_image_guidance_fields(reference_image))

    return {
        "ok": True,
        "phase": PHASE_26D,
        "service": SERVICE_NAME,
        "mode": "product-plan-generator",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Image-guided product plan generated from safe metadata." if reference_image else "Product plan generated. Preview generation and code generation remain approval-gated for later phases."
        },
        "plan": plan,
        "next": {
            "canGenerateProductPlan": True,
            "canGeneratePreview": False,
            "canGenerateCode": False,
            "approvalRequiredBeforePreview": True,
            "approvalRequiredBeforeCode": True
        },
        "safety": _phase26d_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_26D,
        "mode": "product-plan-generator",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase26d_safety(),
    }
