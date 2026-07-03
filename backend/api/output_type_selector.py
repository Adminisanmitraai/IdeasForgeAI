import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 27D output type selector"])

PHASE_27D = "27D"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_INPUT_LENGTH = 30000

BLOCKED_PAYLOAD_FIELDS = {
    "file", "files", "upload", "uploads", "image", "images", "photo",
    "photos", "audio", "voice", "blob", "bytes"
}

OUTPUT_TYPE_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Output Type Selector Agent.

Your job is to decide the best output format for a user's idea after sector classification,
requirement expansion, and workflow mapping.

IdeasForgeAI can create or plan:
AI assistant app, website, dashboard, mobile web app, project report, research report,
presentation, catalog, proposal, Excel automation tool, accounts tool, inventory tool,
restaurant tool, retail sales tool, social media content pack, reel script pack,
Instagram post pack, WhatsApp promo pack, household/home-business assistant,
student report, and multi-output business bundles.

Important rules:
- Do not generate code.
- Do not generate files.
- Do not generate real PDF/DOCX/PPTX/Excel yet.
- Do not claim database/auth/upload/OCR/voice/export are active.
- Keep code/export/deployment approval-gated.
- Select the most useful output type for the user's real workflow.
- Recommend multi-output bundles when useful.
- Return JSON only. No markdown. No code fences.

Return:
selectionTitle, primaryOutputType, secondaryOutputTypes, outputBundle,
reasoning, userFacingPromise, recommendedBuildPath, requiredScreens,
requiredDocuments, plannedExports, contentModules, dataModules,
aiAssistantModules, approvalGates, notIncludedYet, priorityOrder,
nextEndpoint, betterThanLovableQualityNotes.
"""


def _phase27d_safety() -> dict:
    flags = safety_flags()
    flags["sectorClassificationEnabled"] = True
    flags["requirementExpansionEnabled"] = True
    flags["workflowMappingEnabled"] = True
    flags["outputTypeSelectionEnabled"] = True
    flags["productGenerationEnabled"] = True
    flags["previewGenerationEnabled"] = True
    flags["approvalGateEnabled"] = True
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


def _fallback_output_selection(idea: str, classification: dict, requirements: dict, workflow: dict) -> dict:
    sector = "general professional workflow"
    if isinstance(classification, dict):
        sector = classification.get("primarySector", sector)
    if isinstance(requirements, dict):
        sector = requirements.get("sector", sector)

    text = idea.lower()

    primary = "AI assistant app"
    secondary = ["dashboard", "report"]
    bundle = "professional AI assistant + dashboard + report plan"

    if any(word in text for word in ["presentation", "ppt", "slides"]):
        primary = "presentation"
        secondary = ["report", "speaker notes"]
        bundle = "presentation + report bundle"
    elif any(word in text for word in ["catalog", "menu", "brochure"]):
        primary = "catalog"
        secondary = ["PDF layout plan", "social promo content"]
        bundle = "catalog + promo content bundle"
    elif any(word in text for word in ["reel", "instagram", "promo", "caption"]):
        primary = "social media content pack"
        secondary = ["reel scripts", "Instagram captions", "content calendar"]
        bundle = "content creator promo bundle"
    elif any(word in text for word in ["excel", "reconcile", "sheet"]):
        primary = "Excel automation assistant"
        secondary = ["exception report", "dashboard"]
        bundle = "Excel automation + reconciliation report bundle"
    elif any(word in text for word in ["restaurant", "tiffin", "orders", "menu"]):
        primary = "business operations assistant app"
        secondary = ["dashboard", "Instagram promo pack", "weekly report"]
        bundle = "home food business assistant + dashboard + promo content bundle"

    return {
        "selectionTitle": "IdeasForgeAI Output Type Selection",
        "primaryOutputType": primary,
        "secondaryOutputTypes": secondary,
        "outputBundle": bundle,
        "reasoning": [
            "The user's idea needs a practical workflow tool, not only static content.",
            "The selected output supports daily use, review, and future automation.",
            "Secondary outputs help the user present, report, or promote the workflow."
        ],
        "userFacingPromise": "IdeasForgeAI will turn this idea into a practical, approval-gated professional output plan.",
        "recommendedBuildPath": [
            "Confirm output type",
            "Generate product plan",
            "Generate preview specification",
            "Use approval gate before code/export/deployment"
        ],
        "requiredScreens": [
            "Idea intake",
            "Workflow dashboard",
            "Review screen",
            "Approval gate"
        ],
        "requiredDocuments": [
            "Future PDF report plan",
            "Future export plan"
        ],
        "plannedExports": [
            "PDF later",
            "DOCX later",
            "PPTX later",
            "Excel later"
        ],
        "contentModules": [
            "Summary copy",
            "Instruction text",
            "Report/promo content where relevant"
        ],
        "dataModules": [
            "Input records",
            "Status tracking",
            "Review state"
        ],
        "aiAssistantModules": [
            "Workflow assistant",
            "Summary generator",
            "Recommendation helper"
        ],
        "approvalGates": {
            "beforeProductPlan": False,
            "beforePreview": False,
            "beforeCodeGeneration": True,
            "beforeExport": True,
            "beforeDeployment": True
        },
        "notIncludedYet": [
            "Actual code generation",
            "Actual file exports",
            "Database",
            "Authentication",
            "Upload/OCR/voice",
            "Deployment"
        ],
        "priorityOrder": [
            "Primary output type",
            "Daily workflow",
            "Dashboard/report needs",
            "Approval gate",
            "Future exports"
        ],
        "nextEndpoint": "/api/product-plan",
        "betterThanLovableQualityNotes": [
            "Select output based on real workflow, not generic app type",
            "Support multi-output business bundles",
            "Keep safety and approval gates clear",
            "Plan mobile-first professional usage"
        ]
    }


@router.post("/output-type")
async def select_output_type(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 27D"),
        )

    idea = payload.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    idea = idea.strip()
    classification = payload.get("classification") or {}
    requirements = payload.get("requirements") or {}
    workflow = payload.get("workflow") or {}
    user_goal = _safe_text(payload.get("userGoal"))

    input_size = (
        len(idea)
        + len(json.dumps(classification, ensure_ascii=False, default=str))
        + len(json.dumps(requirements, ensure_ascii=False, default=str))
        + len(json.dumps(workflow, ensure_ascii=False, default=str))
    )

    if input_size > MAX_INPUT_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"output type input must be {MAX_INPUT_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"output-type-{uuid4().hex[:12]}"

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27D,
                "mode": "output-type-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Output Type Selector is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase27d_safety(),
            },
        )

    prompt = {
        "task": "Select the best output type or multi-output bundle for this IdeasForgeAI use case.",
        "idea": idea,
        "classification": classification,
        "requirements": requirements,
        "workflow": workflow,
        "userGoal": user_goal or "infer",
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
            instructions=OUTPUT_TYPE_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False, default=str),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            selection = json.loads(output_text)
        except Exception:
            selection = _fallback_output_selection(
                idea,
                classification if isinstance(classification, dict) else {},
                requirements if isinstance(requirements, dict) else {},
                workflow if isinstance(workflow, dict) else {},
            )
            selection["rawAIOutputSelection"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "OUTPUT_TYPE_SELECTION_FAILURE", "Output type selection failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_27D,
        "service": SERVICE_NAME,
        "mode": "output-type-selection",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Output type selected. Product planning, preview planning, and approval gates remain controlled."
        },
        "outputSelection": selection,
        "next": {
            "canClassifySector": True,
            "canExpandRequirements": True,
            "canMapWorkflow": True,
            "canSelectOutputType": True,
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "recommendedNextEndpoint": "/api/product-plan",
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase27d_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27D,
        "mode": "output-type-selection",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase27d_safety(),
    }

