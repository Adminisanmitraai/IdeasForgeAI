import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 27C workflow mapping"])

PHASE_27C = "27C"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_INPUT_LENGTH = 26000

BLOCKED_PAYLOAD_FIELDS = {
    "file", "files", "upload", "uploads", "image", "images", "photo",
    "photos", "audio", "voice", "blob", "bytes"
}

WORKFLOW_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Workflow Mapping Agent.

Your job is to convert a user idea, sector classification, and expanded requirements into a clear step-by-step workflow map.

IdeasForgeAI supports AI assistants, apps, dashboards, reports, presentations, catalogs, proposals,
student reports, research reports, retail/account/inventory tools, restaurant tools, farming tools,
social media/reels tools, home business tools, and daily work automation tools.

Important rules:
- Do not generate code.
- Do not generate preview HTML/CSS/JS.
- Do not write files.
- Do not claim database/auth/upload/OCR/voice/export are active.
- Keep code/export/deployment approval-gated.
- Make workflow practical enough for a real user to understand and later build.
- Make output more professional and production-useful than generic app builder output.
- Return JSON only. No markdown. No code fences.

Return:
workflowTitle, sector, userRole, workflowSummary, actors, inputFlow, mainWorkflowSteps,
aiDecisionPoints, manualReviewPoints, exceptionFlows, screensTouched, dataCaptured,
outputsCreated, approvalGates, statusStates, notifications, futureAutomationHooks,
notIncludedYet, acceptanceCriteria, nextEndpoint.
"""


def _phase27c_safety() -> dict:
    flags = safety_flags()
    flags["sectorClassificationEnabled"] = True
    flags["requirementExpansionEnabled"] = True
    flags["workflowMappingEnabled"] = True
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


def _fallback_workflow(idea: str, classification: dict, requirements: dict, user_role: str) -> dict:
    sector = "general professional workflow"
    if isinstance(classification, dict):
        sector = classification.get("primarySector", sector)
    if isinstance(requirements, dict):
        sector = requirements.get("sector", sector)

    return {
        "workflowTitle": "IdeasForgeAI Workflow Map",
        "sector": sector,
        "userRole": user_role or "professional user",
        "workflowSummary": "A practical approval-gated workflow that converts the user's manual work into an AI-assisted process.",
        "actors": [
            "User",
            "IdeasForgeAI assistant",
            "Reviewer / approver"
        ],
        "inputFlow": [
            "User describes the work",
            "System classifies sector and role",
            "System expands requirements",
            "System maps workflow steps"
        ],
        "mainWorkflowSteps": [
            {
                "step": 1,
                "name": "Idea intake",
                "userAction": "Describe the work or goal",
                "aiAction": "Understand sector, role, and output type",
                "result": "Structured intake summary"
            },
            {
                "step": 2,
                "name": "Requirement review",
                "userAction": "Review missing questions and assumptions",
                "aiAction": "Expand requirements into screens, inputs, outputs, and rules",
                "result": "Approval-ready requirement blueprint"
            },
            {
                "step": 3,
                "name": "Workflow mapping",
                "userAction": "Confirm daily workflow and review points",
                "aiAction": "Create step-by-step user and AI actions",
                "result": "Workflow map"
            },
            {
                "step": 4,
                "name": "Product plan handoff",
                "userAction": "Approve workflow for product planning",
                "aiAction": "Prepare product-plan-ready structure",
                "result": "Ready for /api/product-plan"
            }
        ],
        "aiDecisionPoints": [
            "Detect sector and assistant category",
            "Identify missing information",
            "Suggest output format",
            "Highlight review/approval points"
        ],
        "manualReviewPoints": [
            "Before preview generation",
            "Before code generation",
            "Before export",
            "Before deployment"
        ],
        "exceptionFlows": [
            "Missing required information",
            "User rejects assumptions",
            "Sensitive sector requires manual review",
            "Unsupported upload/export request is blocked"
        ],
        "screensTouched": [
            "Chat intake",
            "Requirements review",
            "Workflow map",
            "Approval gate"
        ],
        "dataCaptured": [
            "idea",
            "sector",
            "user role",
            "workflow type",
            "output goal",
            "approval state"
        ],
        "outputsCreated": [
            "workflow map",
            "review checklist",
            "product plan input"
        ],
        "approvalGates": {
            "beforeProductPlan": False,
            "beforePreview": False,
            "beforeCodeGeneration": True,
            "beforeExport": True,
            "beforeDeployment": True
        },
        "statusStates": [
            "draft",
            "needs review",
            "approved for product plan",
            "blocked for code generation"
        ],
        "notifications": [
            "Missing information alert",
            "Approval required alert",
            "Code generation blocked status"
        ],
        "futureAutomationHooks": [
            "Database later",
            "File upload later",
            "Export engine later",
            "Auth later"
        ],
        "notIncludedYet": [
            "Code generation",
            "File writes",
            "Database",
            "Authentication",
            "Upload/OCR/voice",
            "Export generation",
            "Deployment"
        ],
        "acceptanceCriteria": [
            "Workflow steps are clear",
            "User and AI actions are separated",
            "Review points are visible",
            "Code generation remains disabled"
        ],
        "nextEndpoint": "/api/product-plan"
    }


@router.post("/workflow-map")
async def map_workflow(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 27C"),
        )

    idea = payload.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    idea = idea.strip()
    classification = payload.get("classification") or {}
    requirements = payload.get("requirements") or {}
    user_role = _safe_text(payload.get("userRole"))

    input_size = (
        len(idea)
        + len(json.dumps(classification, ensure_ascii=False, default=str))
        + len(json.dumps(requirements, ensure_ascii=False, default=str))
    )

    if input_size > MAX_INPUT_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"workflow input must be {MAX_INPUT_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"workflow-map-{uuid4().hex[:12]}"

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27C,
                "mode": "workflow-map-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Workflow Mapping Agent is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase27c_safety(),
            },
        )

    prompt = {
        "task": "Create a detailed workflow map for this IdeasForgeAI use case.",
        "idea": idea,
        "classification": classification,
        "requirements": requirements,
        "userRole": user_role or "infer",
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
            instructions=WORKFLOW_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False, default=str),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            workflow = json.loads(output_text)
        except Exception:
            workflow = _fallback_workflow(
                idea,
                classification if isinstance(classification, dict) else {},
                requirements if isinstance(requirements, dict) else {},
                user_role,
            )
            workflow["rawAIWorkflow"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "WORKFLOW_MAPPING_FAILURE", "Workflow mapping failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_27C,
        "service": SERVICE_NAME,
        "mode": "workflow-mapping",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Workflow map generated. Product planning, preview planning, and approval gates remain controlled."
        },
        "workflow": workflow,
        "next": {
            "canClassifySector": True,
            "canExpandRequirements": True,
            "canMapWorkflow": True,
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "recommendedNextEndpoint": "/api/product-plan",
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase27c_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27C,
        "mode": "workflow-mapping",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase27c_safety(),
    }
