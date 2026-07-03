import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.product_flow import create_product_plan, normalize_reference_image_metadata
from backend.sector_router import route_sector
from backend.sector_templates import create_sector_template
from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 27E product flow orchestrator"])

PHASE_27E = "27E"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 60
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_INPUT_LENGTH = 32000

BLOCKED_PAYLOAD_FIELDS = {
    "file", "files", "upload", "uploads", "image", "images", "photo",
    "photos", "audio", "voice", "blob", "bytes"
}

ORCHESTRATOR_SYSTEM_INSTRUCTION = """
You are the IdeasForgeAI Product Flow Orchestrator Agent.

Your job is to connect the planning chain into one professional app-building flow.

Planning chain:
1. sector classification
2. requirement expansion
3. workflow mapping
4. output type selection
5. product plan
6. preview plan
7. approval gate summary

IdeasForgeAI supports:
apps, websites, dashboards, mobile web apps, project reports, research reports, presentations,
catalogs, proposals, Excel tools, accounts tools, inventory tools, restaurant tools, retail tools,
student reports, social media content packs, reels, Instagram posts, WhatsApp promos,
home business tools, farming tools, office automation, and professional AI assistants.

Important rules:
- Do not generate code.
- Do not generate HTML/CSS/JS.
- Do not write files.
- Do not generate real PDF/DOCX/PPTX/Excel exports.
- Do not claim database/auth/upload/OCR/voice/export/deployment are active.
- If referenceImage metadata is provided, mark the flow as image-guided and use it only as layout/style guidance.
- Do not claim image pixels were analyzed. Use metadata, user notes, and safe inference only.
- Keep code/export/deployment approval-gated.
- Produce a clean orchestrated plan better than generic app builders.
- Make the plan sector-specific. For car detailing include service packages, doorstep booking,
  before-after gallery, booking calendar, payment status, admin dashboard, daily bookings,
  revenue, and customer leads. For gyms include membership plans, trainer profiles,
  class booking, attendance tracking, diet consultation, payment dashboard, and member records.
  For wedding/event lawns include wedding packages, Haldi theme, Mehendi theme, gallery,
  booking calendar, enquiry form, admin lead dashboard, package comparison, India-friendly
  labels such as Lawn Booking, Banquet Package, Booking Lead, and Indian rupee pricing.
  For restaurants include menu cards, table booking, order summary, popular dishes,
  owner dashboard, and reservations. For clinics include calm doctor profiles, treatment
  packages, appointment booking, patient enquiry, and admin schedule. For schools include
  parent dashboard, notices, fees, homework, attendance, exam results, and teacher contact.
  For retail include inventory dashboard, stock cards, low-stock alerts, sales records,
  revenue dashboard, and product cards.
- Avoid stale generic preview wording such as AI Product Builder, Active users, and Open tasks
  unless the user's requested product is actually a builder/admin SaaS tool.
- Keep runtime API integrations backend-proxy-only and never place real API keys in generated frontend plans.
- Include visualThemeFamily, layoutVariant, and a short designInspirationNote in the flow so generated apps avoid repetitive generic styling.
- Agriculture/farmer ideas must take priority over clinic/healthcare; crop health, farm health, and soil health are agriculture signals, not clinic signals.
- Classify clinic only for clear clinic terms such as clinic, doctor, patient, appointment, hospital, dental, treatment, prescription, queue, or OPD.
- Return JSON only. No markdown. No code fences.

Return:
flowTitle, ideaSummary, detectedSector, userRole, selectedOutputType,
planningChain, requirementsSummary, workflowSummary, outputBundle,
productPlanSummary, previewPlanSummary, approvalGateSummary,
recommendedNextEndpoint, frontendFlowSteps, backendFlowSteps,
qualityChecklist, notIncludedYet, safetyRules, stageGateStatus,
betterThanLovableQualityNotes.
"""


def _phase27e_safety() -> dict:
    flags = safety_flags()
    flags["sectorClassificationEnabled"] = True
    flags["requirementExpansionEnabled"] = True
    flags["workflowMappingEnabled"] = True
    flags["outputTypeSelectionEnabled"] = True
    flags["productFlowOrchestrationEnabled"] = True
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


def _client_currency_metadata(payload: dict) -> dict:
    client_context = payload.get("client_context") or payload.get("clientContext") or {}
    if not isinstance(client_context, dict):
        client_context = {}
    return {
        "client_locale": _safe_text(
            payload.get("client_locale")
            or payload.get("clientLocale")
            or client_context.get("client_locale")
            or client_context.get("clientLocale")
            or client_context.get("language")
        ),
        "client_timezone": _safe_text(
            payload.get("client_timezone")
            or payload.get("clientTimezone")
            or client_context.get("client_timezone")
            or client_context.get("clientTimezone")
            or client_context.get("timeZone")
        ),
        "currency_hint": _safe_text(payload.get("currency_hint") or payload.get("currencyHint") or client_context.get("currencyHint")),
    }


def _fallback_flow(idea: str, user_role: str, user_goal: str) -> dict:
    sector_result = route_sector(idea)
    sector_template = create_sector_template(sector_result, idea)
    lower_idea = idea.lower()
    agriculture_terms = [
        "farmer", "farm", "farming", "agriculture", "crop", "crop health", "mandi",
        "soil", "weather", "satellite", "ndvi", "farm records", "farmer profile",
        "agri", "kisan", "fpo", "buyer matching", "harvest", "irrigation",
    ]
    mutual_fund_terms = [
        "mutual fund", "sip", "systematic investment plan", "investment advisor",
        "wealth advisor", "portfolio tracker", "kyc", "risk profile", "fund comparison",
        "asset management", "amc", "portfolio", "nav", "investment guidance",
    ]

    sector = "general professional workflow"
    output_type = "AI assistant app + dashboard"
    if any(word in lower_idea for word in agriculture_terms):
        sector = "agriculture and farmer dashboard"
        output_type = "agriculture farm intelligence and farmer dashboard app"
    elif any(word in lower_idea for word in mutual_fund_terms):
        sector = "mutual fund broker and investment advisor"
        output_type = "mutual fund broker and investment advisor customer service app"
    elif any(word in lower_idea for word in ["tiffin", "restaurant", "menu", "grocery", "food"]):
        sector = "restaurant and home food business"
        output_type = "business operations assistant + dashboard + Instagram promo pack"
    elif any(word in lower_idea for word in ["car", "detailing", "washing", "vehicle", "auto"]):
        sector = "car detailing and vehicle service"
        output_type = "premium service booking app + admin revenue dashboard"
    elif any(word in lower_idea for word in ["gym", "fitness", "trainer", "workout", "membership"]):
        sector = "gym and fitness studio"
        output_type = "membership, class booking, and payment dashboard app"
    elif any(word in lower_idea for word in ["wedding", "venue", "lawn", "haldi", "mehendi", "event"]):
        sector = "wedding and event venue"
        output_type = "event package, enquiry, and lead dashboard app"
    elif any(word in lower_idea for word in ["clinic", "doctor", "patient", "appointment", "hospital", "dental", "treatment", "prescription", "queue", "opd"]):
        sector = "clinic and appointment booking"
        output_type = "appointment booking and admin schedule app"
    elif any(word in lower_idea for word in ["school", "parent", "homework", "attendance", "fees"]):
        sector = "school parent portal"
        output_type = "parent dashboard and school communication app"
    elif any(word in lower_idea for word in ["shop", "retail", "inventory", "stock", "store"]):
        sector = "retail inventory"
        output_type = "inventory, sales, and revenue dashboard app"
    elif any(word in lower_idea for word in ["bank", "reconcile", "excel", "sheet"]):
        sector = "banking and finance operations"
        output_type = "Excel reconciliation assistant + exception report dashboard"
    elif any(word in lower_idea for word in ["student", "project report", "presentation", "ppt"]):
        sector = "student and education"
        output_type = "project report + presentation bundle"

    return {
        "flowTitle": "IdeasForgeAI Product Flow",
        "ideaSummary": idea,
        "sector_id": sector_result["sector_id"],
        "sector_confidence": sector_result["confidence"],
        "sector_reasons": sector_result["reasons"],
        "sector_top_candidates": sector_result["top_candidates"],
        "theme_family": sector_result["theme_family"],
        "layout_family": sector_result["layout_family"],
        "clarification_needed": sector_result["clarification_needed"],
        "clarification_prompt": sector_result["clarification_prompt"],
        "clickable_aliases": sector_template["clickable_aliases"],
        "detectedSector": sector,
        "userRole": user_role or "professional user",
        "selectedOutputType": output_type,
        "planningChain": [
            {"step": 1, "agent": "Sector Classifier", "endpoint": "/api/sector-classifier", "status": "planned/available"},
            {"step": 2, "agent": "Requirement Expansion", "endpoint": "/api/requirements", "status": "planned/available"},
            {"step": 3, "agent": "Workflow Mapping", "endpoint": "/api/workflow-map", "status": "planned/available"},
            {"step": 4, "agent": "Output Type Selector", "endpoint": "/api/output-type", "status": "planned/available"},
            {"step": 5, "agent": "Product Plan Generator", "endpoint": "/api/product-plan", "status": "planned/available"},
            {"step": 6, "agent": "Preview Generator", "endpoint": "/api/preview-plan", "status": "planned/available"},
            {"step": 7, "agent": "Approval Gate", "endpoint": "/api/approval-gate", "status": "required before code/export/deployment"}
        ],
        "requirementsSummary": [
            "Capture user's work goal",
            "Identify inputs, outputs, screens, review points, and missing questions",
            "Keep every high-risk action approval-gated"
        ],
        "workflowSummary": [
            "User submits idea",
            "System creates planning chain",
            "User reviews generated flow",
            "System blocks code/export/deployment until approved"
        ],
        "outputBundle": [
            output_type,
            "workflow dashboard",
            "future report/export plan"
        ],
        "productPlanSummary": [
            "Product plan should use the selected output bundle",
            "Screens and modules should match the real workflow",
            "Mobile-first usage should be prioritized"
        ],
        "previewPlanSummary": [
            "Preview should show intake, dashboard, workflow, outputs, and approval gate",
            "Preview remains planning-only in this phase"
        ],
        "approvalGateSummary": {
            "productPlanAllowed": True,
            "previewAllowed": True,
            "codeGenerationAllowed": False,
            "exportAllowed": False,
            "deploymentAllowed": False
        },
        "recommendedNextEndpoint": "/api/product-plan",
        "frontendFlowSteps": [
            "User enters idea in chat",
            "Show detected sector and output type",
            "Show requirement/workflow summary",
            "Show Generate Product Plan",
            "Show Generate Preview only after plan"
        ],
        "backendFlowSteps": [
            "Classify sector",
            "Expand requirements",
            "Map workflow",
            "Select output type",
            "Generate product plan",
            "Generate preview plan",
            "Check approval gate"
        ],
        "qualityChecklist": [
            "Sector-aware",
            "Workflow-specific",
            "Mobile-ready",
            "Approval-gated",
            "No code generation yet"
        ],
        "notIncludedYet": [
            "Actual code generation",
            "Actual file exports",
            "Database",
            "Authentication",
            "Upload/OCR/voice",
            "Deployment"
        ],
        "safetyRules": [
            "No frontend API keys",
            "No code generation in Phase 27E",
            "No export generation in Phase 27E",
            "Human approval before code/export/deployment"
        ],
        "stageGateStatus": "Ready for product-plan and preview-plan, blocked for code/export/deployment.",
        "betterThanLovableQualityNotes": [
            "Uses full planning chain before generation",
            "Chooses output based on real work use case",
            "Keeps quality checklist and safety gates visible",
            "Plans multi-output professional bundles"
        ],
        "visualThemeFamily": "agriculture-green-dashboard" if sector == "agriculture and farmer dashboard" else "finance-trust-blue" if sector == "mutual fund broker and investment advisor" else "generic-modern-saas",
        "layoutVariant": "hero-stat-stack" if sector == "agriculture and farmer dashboard" else "card-first-dashboard",
        "designInspirationNote": (
            "Use a green, earthy, farmer-friendly mobile dashboard with crop health, weather, mandi, satellite intelligence, profile, farm records, and AI chat cards."
            if sector == "agriculture and farmer dashboard"
            else "Use a sector-appropriate visual theme, palette, layout rhythm, and card style instead of a generic repeated app shell."
        )
    }


@router.post("/product-flow")
async def orchestrate_product_flow(request: Request):
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
            content=validation_error("raw file, image, audio, and upload payloads are disabled; send referenceImage metadata only"),
        )

    message = payload.get("message")
    mode = _safe_text(payload.get("mode"))
    if isinstance(message, str) and message.strip() and mode in {"local-product-plan", "app_creation"}:
        message = message.strip()
        plan = create_product_plan(
            message,
            reference_image=normalize_reference_image_metadata(payload),
            client_metadata=_client_currency_metadata(payload),
        )
        return {
            "ok": True,
            "reply": "I created a structured product plan. Review it, then approve generation when you are ready.",
            "plan": plan,
            "next_action": "approve_generate",
        }

    idea = payload.get("idea")
    if not isinstance(idea, str) or not idea.strip():
        return JSONResponse(status_code=400, content=validation_error("idea is required"))

    idea = idea.strip()
    has_orchestration_context = any(
        payload.get(key)
        for key in ["classification", "requirements", "workflow", "outputSelection", "userRole", "userGoal"]
    )
    if not has_orchestration_context or mode in {"local-product-plan", "structured-product-plan", "app_creation"}:
        plan = create_product_plan(
            idea,
            reference_image=normalize_reference_image_metadata(payload),
            client_metadata=_client_currency_metadata(payload),
        )
        return {
            "ok": True,
            "reply": "I created a structured product plan. Review it, then approve generation when you are ready.",
            "plan": plan,
            "next_action": "approve_generate",
        }

    user_role = _safe_text(payload.get("userRole"))
    user_goal = _safe_text(payload.get("userGoal"))
    classification = payload.get("classification") or {}
    requirements = payload.get("requirements") or {}
    workflow = payload.get("workflow") or {}
    output_selection = payload.get("outputSelection") or {}
    reference_image = normalize_reference_image_metadata(payload)
    sector_result = route_sector(idea, reference_image=reference_image, locale_currency_metadata=_client_currency_metadata(payload))

    input_size = (
        len(idea)
        + len(user_role)
        + len(user_goal)
        + len(json.dumps(classification, ensure_ascii=False, default=str))
        + len(json.dumps(requirements, ensure_ascii=False, default=str))
        + len(json.dumps(workflow, ensure_ascii=False, default=str))
        + len(json.dumps(output_selection, ensure_ascii=False, default=str))
        + len(json.dumps(reference_image, ensure_ascii=False, default=str))
    )

    if input_size > MAX_INPUT_LENGTH:
        return JSONResponse(
            status_code=413,
            content=validation_error(
                f"product flow input must be {MAX_INPUT_LENGTH} characters or fewer",
                code="PAYLOAD_TOO_LARGE",
            ),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"product-flow-{uuid4().hex[:12]}"

    if not is_openai_configured():
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "phase": PHASE_27E,
                "mode": "product-flow-not-configured",
                "sessionId": session_id,
                "assistant": {
                    "role": "assistant",
                    "content": "Product Flow Orchestrator is ready, but OPENAI_API_KEY is not configured on the backend."
                },
                "error": {
                    "code": "OPENAI_NOT_CONFIGURED",
                    "message": "OPENAI_API_KEY is missing from the backend environment."
                },
                "safety": _phase27e_safety(),
            },
        )

    prompt = {
        "task": "Create an orchestrated product flow for this IdeasForgeAI use case.",
        "idea": idea,
        "userRole": user_role or "infer",
        "userGoal": user_goal or "infer",
        "classification": classification,
        "sectorRouter": sector_result,
        "sectorTemplate": create_sector_template(sector_result, idea, reference_image),
        "requirements": requirements,
        "workflow": workflow,
        "outputSelection": output_selection,
        "inputMode": "image-guided" if reference_image else "text-only",
        "referenceImage": reference_image,
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
            instructions=ORCHESTRATOR_SYSTEM_INSTRUCTION,
            input=json.dumps(prompt, ensure_ascii=False, default=str),
        )

        output_text = _strip_json_fence(response.output_text)

        try:
            flow = json.loads(output_text)
        except Exception:
            flow = _fallback_flow(idea, user_role, user_goal)
            flow["rawAIFlow"] = output_text

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
        return JSONResponse(status_code=500, content=_agent_error(session_id, "PRODUCT_FLOW_FAILURE", "Product flow orchestration failed safely. Try again shortly."))

    return {
        "ok": True,
        "phase": PHASE_27E,
        "service": SERVICE_NAME,
        "mode": "product-flow-orchestration",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Product flow orchestrated. Code generation, export, deployment, database, upload, OCR, and voice remain disabled."
        },
        "flow": flow,
        "sector_router": sector_result,
        "next": {
            "canClassifySector": True,
            "canExpandRequirements": True,
            "canMapWorkflow": True,
            "canSelectOutputType": True,
            "canOrchestrateProductFlow": True,
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "recommendedNextEndpoint": "/api/product-plan",
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True
        },
        "safety": _phase27e_safety(),
    }


def _agent_error(session_id: str, code: str, message: str) -> dict:
    return {
        "ok": False,
        "phase": PHASE_27E,
        "mode": "product-flow-orchestration",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": message,
        },
        "error": {
            "code": code,
            "message": message,
        },
        "safety": _phase27e_safety(),
    }

