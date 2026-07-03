import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 27B requirement expansion"])

PHASE_27B = "27B"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_INPUT_LENGTH = 20000

BLOCKED_PAYLOAD_FIELDS = {
    "file", "files", "upload", "uploads", "image", "images", "photo",
    "photos", "audio", "voice", "blob", "bytes"
}

REQUIREMENT_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Requirement Expansion Agent.

Your job is to convert a user idea and sector classification into detailed, practical, approval-ready requirements.

IdeasForgeAI supports professional AI assistants, apps, dashboards, reports, presentations, catalogs, proposals,
student reports, research reports, retail/account/inventory tools, restaurant tools, farming tools, social media/reels tools,
home business tools, and daily work automation tools.

Important rules:
- Do not generate code.
- Do not generate preview UI.
- Do not write files.
- Do not claim database/auth/upload/OCR/voice/export are active.
- Keep everything approval-gated.
- Make the output better than generic app builder output.
- Return JSON only. No markdown. No code fences.

Return:
requirementTitle, sector, userRole, outputType, problemSummary, expandedGoal,
dailyWorkflow, userInputs, dataFields, aiTasks, manualReviewPoints, outputs,
screensNeeded, reportsOrExportsNeeded, futureIntegrations, missingQuestions,
assumptions, safetyRequirements, acceptanceCriteria, priorityFeatures,
phaseRecommendation, nextEndpoint.
"""


def _phase27b_safety() -> dict:
    flags = safety_flags()
    flags["sectorClassificationEnabled"] = True
    flags["requirementExpansionEnabled"] = True
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


def _fallback_requirements(idea: str, classification: dict, user_role: str, output_goal: str) -> dict:
    sector = "general professional workflow"
    if isinstance(classification, dict):
        sector = classification.get("primarySector", sector)

    return {
        "requirementTitle": "IdeasForgeAI Requirement Blueprint",
        "sector": sector,
        "userRole": user_role or classification.get("userRole", "professional user") if isinstance(classification, dict) else user_role or "professional user",
        "outputType": output_goal or "AI assistant app",
        "problemSummary": idea,
        "expandedGoal": "Create a practical AI assistant that turns the user's repeated manual workflow into a structured, reviewable, approval-gated tool.",
        "dailyWorkflow": [
            "User enters or imports daily work context",
            "AI organizes the work into steps",
            "System highlights missing data and exceptions",
            "User reviews and approves the final output"
        ],
        "userInputs": [
            "User idea",
            "Sector",
            "Current workflow",
            "Expected final output"
        ],
        "dataFields": [
            "task name",
            "date",
            "category",
            "status",
            "remarks",
            "approval status"
        ],
        "aiTasks": [
            "Understand the workflow",
            "Structure missing requirements",
            "Suggest professional output format",
            "Prepare review-ready summary"
        ],
        "manualReviewPoints": [
            "Before preview generation",
            "Before code generation",
            "Before export",
            "Before deployment"
        ],
        "outputs": [
            "Expanded requirements",
            "Workflow checklist",
            "Product plan input",
            "Preview planning input"
        ],
        "screensNeeded": [
            "Idea intake",
            "Requirements summary",
            "Workflow mapping",
            "Review and approval"
        ],
        "reportsOrExportsNeeded": [
            "Future PDF/DOCX/PPTX/Excel export plan"
        ],
        "futureIntegrations": [
            "Database later",
            "File upload later",
            "Export engine later",
            "Auth later"
        ],
        "missingQuestions": [
            "What exact inputs does the user currently use?",
            "What final output is needed?",
            "Who approves the result?",
            "How often will this tool be used?"
        ],
        "assumptions": [
            "User wants a practical tool, not just a document",
            "Human approval is required before final action"
        ],
        "safetyRequirements": [
            "No code generation in Phase 27B",
            "No upload/OCR/voice/database/auth/export in Phase 27B",
            "Human approval required before code/export/deployment"
        ],
        "acceptanceCriteria": [
            "Requirements clearly explain the workflow",
            "Inputs and outputs are identified",
            "Missing questions are listed",
            "Next endpoint is recommended"
        ],
        "priorityFeatures": [
            "Workflow mapping",
            "Input/output planning",
            "Approval gates",
            "Professional summary"
        ],
        "phaseRecommendation": "Continue to /api/product-plan after requirements are accepted.",
        "nextEndpoint": "/api/product-plan"
    }


@router.post("/requirements")
async def expand_requirements(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 27B"),
        )

    idea = payload.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    idea = idea.strip()
    classification = payload.get("classification") or {}
    user_role = _safe_text(payload.get("userRole"))
    output_goal = _safe_text(payload.get("outputGoal"))

    input_size = len(idea) + len(json.dumps(classification, ensure_ascii=False, default=str))
    if input_size > MAX_INPUT_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"requirement input must be {MAX_INPUT_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"requirements-{uuid4().hex[:12]}"

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27B,
                "mode": "requirements-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Requirement Expansion Agent is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase27b_safety(),
            },
        )

    prompt = {
        "task": "Expand this IdeasForgeAI idea into detailed requirements.",
        "idea": idea,
        "classification": classification,
        "userRole": user_role or "infer",
        "outputGoal": output_goal or "infer",
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
            instructions=REQUIREMENT_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False, default=str),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            requirements = json.loads(output_text)
        except Exception:
            requirements = _fallback_requirements(idea, classification if isinstance(classification, dict) else {}, user_role, output_goal)
            requirements["rawAIRequirements"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "REQUIREMENT_EXPANSION_FAILURE", "Requirement expansion failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_27B,
        "service": SERVICE_NAME,
        "mode": "requirement-expansion",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Requirements expanded. Product planning, preview planning, and approval gates remain controlled."
        },
        "requirements": requirements,
        "next": {
            "canClassifySector": True,
            "canExpandRequirements": True,
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "recommendedNextEndpoint": "/api/product-plan",
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase27b_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27B,
        "mode": "requirement-expansion",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase27b_safety(),
    }

