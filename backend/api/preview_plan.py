import json
import os
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.product_flow import resolve_currency_profile
from backend.sector_router import route_sector
from backend.sector_templates import create_sector_template
from backend.utils.safe_response import is_openai_configured, safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 26E preview generator"])

PHASE_26E = "26E"
SERVICE_NAME = "ideasforgeai-backend"
OPENAI_TIMEOUT_SECONDS = 45
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
MAX_PREVIEW_INPUT_LENGTH = 20000
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
- If referenceImage metadata is provided, mark the preview as image-guided and use it only as layout/style guidance.
- Do not claim image pixels were analyzed. Use metadata, user notes, and safe inference only.
- Include visualThemeFamily, layoutVariant, and a short designInspirationNote so generated previews avoid repetitive generic styling.
- Agriculture/farmer ideas must take priority over clinic/healthcare. Crop health, farm health, and soil health mean agriculture.
- Classify clinic only when clear clinic terms are present: clinic, doctor, patient, appointment, hospital, dental, treatment, prescription, queue, or OPD.
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


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    return text


def _normalize_reference_image(payload: dict) -> dict:
    raw = None
    for key in REFERENCE_IMAGE_KEYS:
        if key in payload:
            raw = payload.get(key)
            break

    if not isinstance(raw, dict) and isinstance(payload.get("productPlan"), dict):
        raw = payload["productPlan"].get("referenceImage")

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


def _image_guided_preview_fields(reference_image: dict) -> dict:
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
        "referenceImageSummary": (
            f"Preview is guided by {source_label} metadata for layout, rhythm, hierarchy, and mobile interface feel. "
            "No image bytes, OCR, or pixel analysis are used in this phase."
        ),
        "designDirection": {
            "style": "reference-inspired, mobile-first, app-interface-aware",
            "layout": "phone-sized surface with top status/header, high-signal content bands, compact cards, and clear bottom actions",
            "tone": "polished, practical, visual-reference-aware",
        },
        "mobileExperience": [
            "Reference-inspired first screen",
            "App-like header and navigation hierarchy",
            "Dense but readable card/list sections",
            "Sticky primary action area suitable for iPhone-sized screens",
        ],
        "visualPolishNotes": [
            "Use the reference metadata to guide spacing and hierarchy",
            "Prefer mobile app interface patterns over generic landing-page sections",
            "Keep card radius, contrast, and tap targets consistent",
            "State clearly that full vision automation is not enabled yet",
        ],
        "designInspirationNote": "Reference metadata guides layout rhythm, hierarchy, spacing, and mobile interface feel only.",
    }


def _fallback_preview(idea: str, product_plan: dict, sector: str, output_type: str, reference_image: dict | None = None) -> dict:
    sector_result = route_sector(
        f"{idea} {sector} {output_type} {json.dumps(product_plan, ensure_ascii=False, default=str) if isinstance(product_plan, dict) else ''}",
        reference_image=reference_image,
    )
    sector_template = create_sector_template(sector_result, idea, reference_image)
    plan_name = ""
    if isinstance(product_plan, dict):
        plan_name = product_plan.get("productName", "")
    product_plan_text = " ".join(str(value) for value in product_plan.values()) if isinstance(product_plan, dict) else ""
    combined_text = f"{idea} {sector} {output_type} {plan_name} {product_plan_text}".lower()
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
    is_agriculture = any(term in combined_text for term in agriculture_terms)
    is_mutual_fund = any(term in combined_text for term in mutual_fund_terms)

    preview = {
        "previewName": "Farmer Dashboard" if is_agriculture else "Mutual Fund Advisor" if is_mutual_fund else plan_name or "IdeasForgeAI Professional Preview",
        "sector_id": sector_result["sector_id"],
        "sector_confidence": sector_result["confidence"],
        "sector_reasons": sector_result["reasons"],
        "theme_family": sector_result["theme_family"],
        "layout_family": sector_result["layout_family"],
        "clickable_aliases": sector_template["clickable_aliases"],
        "sector": "agriculture and farmer dashboard" if is_agriculture else "mutual fund broker and investment advisor" if is_mutual_fund else sector or product_plan.get("sector", "general professional workflow") if isinstance(product_plan, dict) else sector or "general professional workflow",
        "outputType": "agriculture farm intelligence and farmer dashboard app" if is_agriculture else "mutual fund broker and investment advisor customer service app" if is_mutual_fund else output_type or product_plan.get("outputType", "AI assistant app preview") if isinstance(product_plan, dict) else output_type or "AI assistant app preview",
        "designDirection": {
            "style": "green, earthy, farm-friendly, mobile-first dashboard" if is_agriculture else "professional finance-trust-blue, clean, trustworthy, mobile-first" if is_mutual_fund else "premium, clean, mobile-first, professional",
            "layout": "farmer dashboard cards for crop health, weather, mandi prices, satellite intelligence, profile, farm records, AI chat, and admin recommendations" if is_agriculture else "mutual fund categories, compare funds, SIP calculator, portfolio tracker, KYC upload, risk profile, advisor booking, SIP reminders, and admin dashboard cards" if is_mutual_fund else "chat intake on top, workflow dashboard in center, approval controls at bottom",
            "tone": "simple, farmer-friendly, advisory-focused" if is_agriculture else "clean, trustworthy, finance-oriented, advisor-guidance focused" if is_mutual_fund else "clear, useful, business-ready"
        },
        "mobileExperience": [
            "Simple farmer-friendly mobile dashboard",
            "Crop health, weather, mandi, and satellite cards above the fold",
            "Farmer profile, farm records, and AI chat as large tap targets",
            "Alerts and recommendations visible without clutter"
        ] if is_agriculture else [
            "Mutual fund dashboard with SIP amount, portfolio value, advisory leads, and KYC pending",
            "Fund categories, compare funds, SIP calculator, and portfolio tracker as large tap targets",
            "KYC upload, risk profile, advisor booking, and SIP reminders visible without clutter",
            "Use estimated growth and advisor guidance wording without guaranteed return claims"
        ] if is_mutual_fund else [
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
            "Home Dashboard",
            "Crop Health",
            "Weather",
            "Mandi Prices",
            "Satellite Intelligence",
            "Farmer Profile",
            "Farm Records",
            "AI Chat",
            "Admin Dashboard",
        ] if is_agriculture else [
            "Home Dashboard",
            "Mutual Fund Categories",
            "Compare Funds",
            "SIP Calculator",
            "Portfolio Tracker",
            "KYC Upload",
            "Risk Profile",
            "Advisor Booking",
            "SIP Reminders",
            "Admin Dashboard",
        ] if is_mutual_fund else [
            "Welcome / idea intake screen",
            "Generated product plan screen",
            "Workflow preview screen",
            "Output format preview screen",
            "Approval gate screen"
        ],
        "sections": [
            "Farmer Dashboard",
            "Crop Health",
            "Weather",
            "Mandi Prices",
            "Satellite Intelligence",
            "Farmer Profile",
            "Farm Records",
            "AI Chat"
        ] if is_agriculture else [
            "Mutual Fund Dashboard",
            "Mutual Fund Categories",
            "Compare Funds",
            "SIP Calculator",
            "Portfolio Tracker",
            "KYC Upload",
            "Risk Profile",
            "Advisor Booking",
            "SIP Reminders",
            "Admin Dashboard"
        ] if is_mutual_fund else [
            "Hero summary",
            "Problem solved",
            "Target users",
            "Core workflow",
            "Inputs and outputs",
            "Safety and approval gates"
        ],
        "components": [
            "Crop health cards",
            "Weather cards",
            "Mandi price cards",
            "Satellite intelligence card",
            "Farmer profile card",
            "Farm records cards",
            "AI chat CTA",
            "Alerts and recommendations"
        ] if is_agriculture else [
            "Mutual fund category cards",
            "Compare funds cards",
            "SIP calculator form",
            "Portfolio summary cards",
            "KYC upload checklist",
            "Risk profile form",
            "Advisor booking form",
            "SIP reminder cards",
            "Broker admin dashboard"
        ] if is_mutual_fund else [
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
            "Use green and earthy farm-friendly colors",
            "Use simple farmer-friendly mobile dashboard spacing",
            "Make crop health, weather, mandi, satellite, profile, records, and AI chat cards clickable",
            "Avoid clinic or healthcare visual language"
        ] if is_agriculture else [
            "Use professional finance-trust-blue styling",
            "Use rupee SIP examples such as SIP Amount ₹5,000/mo and Portfolio Value ₹4.6L",
            "Use estimated growth, risk profile, advisor guidance, portfolio summary, and SIP reminder wording",
            "Do not show guaranteed returns, fake KYC approval, fake documents, promised profit, or illegal financial advice",
            "Make compare, funds, sip, portfolio, kyc, risk, advisor, reminders, enquiry, admin, and dashboard targets clickable"
        ] if is_mutual_fund else [
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
        ],
        "visualThemeFamily": "agriculture-green-dashboard" if is_agriculture else "finance-trust-blue" if is_mutual_fund else "generic-modern-saas",
        "layoutVariant": "hero-stat-stack" if is_agriculture else "card-first-dashboard",
        "designInspirationNote": (
            "Use a green, earthy, farmer-friendly mobile dashboard with crop health cards, weather cards, mandi price cards, satellite intelligence, farmer profile, farm records, and AI chat CTA."
            if is_agriculture
            else "Use a professional, clean, trustworthy finance app layout for fund categories, comparison, SIP, portfolio, KYC, risk profile, advisor booking, reminders, and admin workflow."
            if is_mutual_fund
            else "Use a sector-appropriate visual theme, palette, layout rhythm, and card style instead of a generic repeated app shell."
        )
    }
    preview.update(_image_guided_preview_fields(reference_image or {}))
    if reference_image:
        preview["screens"] = [
            "Image-guided mobile home",
            "Reference-inspired dashboard",
            "Primary action flow",
            "Detail/form screen",
            "Approval gate",
        ]
        preview["sections"] = [
            "Status/header area",
            "Primary content band",
            "Compact card/list stack",
            "Sticky action controls",
            "Safety and approval notes",
        ]
        preview["components"] = [
            "Mobile status/header",
            "Reference-guided hero panel",
            "Metric/list cards",
            "Segmented navigation",
            "Bottom primary action",
        ]
    return preview


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
            content=validation_error("raw file, image, audio, and upload payloads are disabled; send referenceImage metadata only"),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"preview-plan-{uuid4().hex[:12]}"

    idea = _safe_text(payload.get("idea"))
    sector = _safe_text(payload.get("sector"))
    output_type = _safe_text(payload.get("outputType"))
    product_plan = payload.get("productPlan") or payload.get("plan")
    reference_image = _normalize_reference_image(payload)
    client_currency = _client_currency_metadata(payload)
    sector_result = route_sector(
        f"{idea} {sector} {output_type} {json.dumps(product_plan, ensure_ascii=False, default=str) if isinstance(product_plan, dict) else ''}",
        reference_image=reference_image,
        locale_currency_metadata=client_currency,
    )
    currency_profile = resolve_currency_profile(f"{idea} {sector} {output_type}", client_currency, detected_domain=sector_result["sector_id"])

    if product_plan is None and not idea:
        return JSONResponse(status_code=400, content=validation_error("productPlan or idea is required"))

    input_size = (
        len(idea)
        + len(json.dumps(product_plan, ensure_ascii=False, default=str))
        + len(json.dumps(reference_image, ensure_ascii=False, default=str))
    )
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
        "sectorRouter": sector_result,
        "sectorTemplate": create_sector_template(sector_result, idea, reference_image),
        "outputType": output_type or "infer best output type",
        "productPlan": product_plan or {},
        "inputMode": "image-guided" if reference_image else "text-only",
        "referenceImage": reference_image,
        "clientCurrencyMetadata": client_currency,
        "currencyProfile": currency_profile,
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
            preview = _fallback_preview(idea, product_plan if isinstance(product_plan, dict) else {}, sector, output_type, reference_image)
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

    if reference_image and isinstance(preview, dict):
        guided_fields = _image_guided_preview_fields(reference_image)
        existing_direction = preview.get("designDirection")
        preview.update(guided_fields)
        if isinstance(existing_direction, dict):
            merged_direction = dict(guided_fields.get("designDirection", {}))
            merged_direction.update(existing_direction)
            preview["designDirection"] = merged_direction
    if isinstance(preview, dict):
        preview.update(
            {
                "sector_id": sector_result["sector_id"],
                "sector_confidence": sector_result["confidence"],
                "sector_reasons": sector_result["reasons"],
                "sector_top_candidates": sector_result["top_candidates"],
                "theme_family": sector_result["theme_family"],
                "layout_family": sector_result["layout_family"],
                "clarification_needed": sector_result["clarification_needed"],
                "clarification_prompt": sector_result["clarification_prompt"],
                "clickable_aliases": create_sector_template(sector_result, idea, reference_image)["clickable_aliases"],
            }
        )
        preview.update(currency_profile)

    return {
        "ok": True,
        "phase": PHASE_26E,
        "service": SERVICE_NAME,
        "mode": "preview-plan-generator",
        "sessionId": session_id,
        "assistant": {
            "role": "assistant",
            "content": "Image-guided preview specification generated from safe metadata." if reference_image else "Preview specification generated. Code generation, export, and deployment remain approval-gated for later phases."
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
