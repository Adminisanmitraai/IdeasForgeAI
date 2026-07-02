import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 27A universal sector classifier"])

PHASE_27A = "27A"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 35
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_IDEA_LENGTH = 12000

BLOCKED_PAYLOAD_FIELDS = {
    "file", "files", "upload", "uploads", "image", "images", "photo",
    "photos", "audio", "voice", "blob", "bytes"
}

SECTOR_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Universal Sector Classifier Agent.

Your job is to read a user's normal-language idea and classify:
1. sector
2. user role
3. workflow type
4. output type
5. best assistant category
6. required next agents
7. safety level
8. missing questions
9. next backend endpoint to use

IdeasForgeAI supports:
banking, finance, share broking, retail, accounts, inventory, restaurants, farming,
creative agencies, sales, data entry, medical admin, education, logistics, real estate,
construction, manufacturing, legal admin, HR, students, research, reports, presentations,
catalogs, social media, reels, Instagram posts, online promos, housewives, home businesses,
online sellers, household productivity, and any professional workflow where AI can assist.

Important:
- Do not generate product plan here.
- Do not generate preview here.
- Do not generate code.
- Do not claim upload/export/database/auth/voice/OCR are active.
- Keep output practical, professional, and better-than-Lovable quality.
- Return JSON only. No markdown. No code fences.
"""


def _phase27a_safety() -> dict:
    flags = safety_flags()
    flags["sectorClassificationEnabled"] = True
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


def _fallback_classification(idea: str, user_role: str, output_goal: str) -> dict:
    text = idea.lower()

    sector = "general professional workflow"
    assistant_category = "professional_work_assistant"

    if any(word in text for word in ["bank", "reconcile", "reconciliation", "transaction"]):
        sector = "banking and finance"
        assistant_category = "reconciliation_assistant"
    elif any(word in text for word in ["restaurant", "menu", "food", "wastage", "kitchen"]):
        sector = "restaurant and food business"
        assistant_category = "restaurant_operations_assistant"
    elif any(word in text for word in ["retail", "shop", "sales", "stock", "inventory"]):
        sector = "retail sales and inventory"
        assistant_category = "retail_inventory_assistant"
    elif any(word in text for word in ["private tutor", "private tutors", "tutor", "tutors", "tuition", "tuition teacher", "coaching class", "private class", "student batch", "student", "school", "teacher", "homework", "attendance", "fees"]):
        sector = "education and tutoring"
        assistant_category = "education_tutor_assistant"
    elif any(word in text for word in ["project report", "research", "assignment", "presentation"]):
        sector = "student and research"
        assistant_category = "student_report_assistant"
    elif any(word in text for word in ["reel", "instagram", "promo", "content", "caption"]):
        sector = "content creator and social media"
        assistant_category = "social_media_content_assistant"
    elif any(word in text for word in ["home", "tiffin", "housewife", "homemaker", "bakery"]):
        sector = "household and home business"
        assistant_category = "home_business_assistant"
    elif any(word in text for word in ["farm", "crop", "farmer", "mandi", "fpo"]):
        sector = "farming and rural business"
        assistant_category = "farming_assistant"

    return {
        "primarySector": sector,
        "secondarySectors": [],
        "userRole": user_role or "professional user",
        "workflowType": "AI-assisted workflow automation",
        "outputTypes": [output_goal or "AI assistant app"],
        "assistantCategory": assistant_category,
        "complexity": "medium",
        "requiredAgents": [
            "Product Plan Generator Agent",
            "Preview Generator Agent",
            "Approval Gate Agent"
        ],
        "recommendedNextEndpoint": "/api/product-plan",
        "safetyLevel": "standard_approval_gated",
        "missingQuestions": [
            "What exact input data does the user have?",
            "What final output should be generated?",
            "Who approves the final result?"
        ],
        "confidence": 0.72,
        "betterThanLovableDirection": [
            "Make the result sector-aware",
            "Map the user's real workflow",
            "Keep output professional and approval-gated",
            "Design for mobile-first practical use"
        ]
    }


@router.post("/sector-classifier")
async def classify_sector(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 27A"),
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
        session_id = f"sector-classifier-{uuid4().hex[:12]}"

    user_role = _safe_text(payload.get("userRole"))
    work_type = _safe_text(payload.get("workType"))
    output_goal = _safe_text(payload.get("outputGoal"))

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27A,
                "mode": "sector-classifier-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Sector Classifier is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase27a_safety(),
            },
        )

    prompt = {
        "task": "Classify this IdeasForgeAI user idea and route it to the right assistant family.",
        "idea": idea,
        "userRole": user_role or "infer",
        "workType": work_type or "infer",
        "outputGoal": output_goal or "infer",
        "requiredJsonShape": {
            "primarySector": "string",
            "secondarySectors": ["string"],
            "userRole": "string",
            "workflowType": "string",
            "outputTypes": ["string"],
            "assistantCategory": "string",
            "complexity": "low | medium | high",
            "requiredAgents": ["string"],
            "recommendedNextEndpoint": "/api/product-plan",
            "safetyLevel": "string",
            "missingQuestions": ["string"],
            "confidence": 0.0,
            "betterThanLovableDirection": ["string"]
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
            instructions=SECTOR_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            classification = json.loads(output_text)
        except Exception:
            classification = _fallback_classification(idea, user_role, output_goal)
            classification["rawAIClassification"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "SECTOR_CLASSIFICATION_FAILURE", "Sector classification failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_27A,
        "service": SERVICE_NAME,
        "mode": "sector-classifier",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Sector, role, output type, and recommended next agent were classified."
        },
        "classification": classification,
        "next": {
            "canClassifySector": True,
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "recommendedNextEndpoint": classification.get("recommendedNextEndpoint", "/api/product-plan") if isinstance(classification, dict) else "/api/product-plan",
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase27a_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27A,
        "mode": "sector-classifier",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase27a_safety(),
    }
