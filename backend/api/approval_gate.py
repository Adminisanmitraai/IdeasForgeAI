from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from backend.utils.safe_response import safety_flags, validation_error

router = APIRouter(prefix="/api", tags=["Phase 26F approval gate"])

PHASE_26F = "26F"
SERVICE_NAME = "ideasforgeai-backend"
MAX_NOTE_LENGTH = 5000

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

SUPPORTED_ACTIONS = {
    "product_plan",
    "preview_generation",
    "code_generation",
    "export_generation",
    "deployment",
}

APPROVAL_REQUIREMENTS = {
    "product_plan": [],
    "preview_generation": ["productPlanApproved"],
    "code_generation": ["productPlanApproved", "previewApproved", "codeGenerationApproved"],
    "export_generation": ["productPlanApproved", "previewApproved", "exportApproved"],
    "deployment": ["productPlanApproved", "previewApproved", "codeGenerationApproved", "deploymentApproved"],
}


def _phase26f_safety() -> dict:
    flags = safety_flags()
    flags["productGenerationEnabled"] = True
    flags["previewGenerationEnabled"] = True
    flags["codeGenerationEnabled"] = False
    flags["approvalGateEnabled"] = True
    return flags


def _is_true(value) -> bool:
    return value is True or value == "true" or value == "yes" or value == "approved"


@router.post("/approval-gate")
async def approval_gate(request: Request):
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
            content=validation_error("file, image, audio, and upload payloads are disabled in Phase 26F"),
        )

    session_id = payload.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"approval-gate-{uuid4().hex[:12]}"

    requested_action = payload.get("requestedAction")
    if not isinstance(requested_action, str) or not requested_action.strip():
        return JSONResponse(status_code=400, content=validation_error("requestedAction is required"))

    requested_action = requested_action.strip()

    if requested_action not in SUPPORTED_ACTIONS:
        return JSONResponse(
            status_code=400,
            content=validation_error(
                "requestedAction must be one of: product_plan, preview_generation, code_generation, export_generation, deployment"
            ),
        )

    approvals = payload.get("approvals") or {}
    if not isinstance(approvals, dict):
        return JSONResponse(status_code=400, content=validation_error("approvals must be a JSON object"))

    user_confirmation = payload.get("userConfirmation")
    if user_confirmation is not None and not isinstance(user_confirmation, str):
        return JSONResponse(status_code=400, content=validation_error("userConfirmation must be a string"))

    note = payload.get("note")
    if note is not None:
        if not isinstance(note, str):
            return JSONResponse(status_code=400, content=validation_error("note must be a string"))
        if len(note) > MAX_NOTE_LENGTH:
            return JSONResponse(
                status_code=413,
                content=validation_error(
                    f"note must be {MAX_NOTE_LENGTH} characters or fewer",
                    code="PAYLOAD_TOO_LARGE",
                ),
            )

    required_keys = APPROVAL_REQUIREMENTS[requested_action]
    missing_approvals = [key for key in required_keys if not _is_true(approvals.get(key))]

    explicit_confirmation_required = requested_action in {
        "code_generation",
        "export_generation",
        "deployment",
    }

    confirmation_ok = True
    if explicit_confirmation_required:
        confirmation_ok = isinstance(user_confirmation, str) and user_confirmation.strip().upper() in {
            "APPROVE",
            "APPROVED",
            "I APPROVE",
            "YES APPROVE",
        }

    approved = not missing_approvals and confirmation_ok

    if requested_action == "product_plan":
        approved = True

    if requested_action == "code_generation":
        allowed_next_step = "Code generation remains blocked in Phase 26F. This gate only records whether approval is ready."
    elif requested_action == "export_generation":
        allowed_next_step = "Export generation remains blocked in Phase 26F. This gate only records whether approval is ready."
    elif requested_action == "deployment":
        allowed_next_step = "Deployment remains blocked in Phase 26F. This gate only records whether approval is ready."
    elif requested_action == "preview_generation":
        allowed_next_step = "Preview generation may proceed only through the existing Phase 26E preview-plan endpoint."
    else:
        allowed_next_step = "Product planning may proceed through the existing Phase 26D product-plan endpoint."

    return {
        "ok": True,
        "phase": PHASE_26F,
        "service": SERVICE_NAME,
        "mode": "approval-gate",
        "sessionId": session_id,
        "requestedAction": requested_action,
        "approved": approved,
        "blocked": not approved or requested_action in {"code_generation", "export_generation", "deployment"},
        "missingApprovals": missing_approvals,
        "explicitConfirmationRequired": explicit_confirmation_required,
        "explicitConfirmationAccepted": confirmation_ok,
        "assistant": {
            "role": "assistant",
            "content": (
                "Approval gate checked. Code generation, export, and deployment remain disabled in Phase 26F."
                if approved
                else "Approval gate blocked this action. Required approvals or explicit confirmation are missing."
            ),
        },
        "next": {
            "canGenerateProductPlan": True,
            "canGeneratePreview": True,
            "canGenerateCode": False,
            "canGenerateExport": False,
            "canDeploy": False,
            "allowedNextStep": allowed_next_step,
            "approvalRequiredBeforeCode": True,
            "approvalRequiredBeforeExport": True,
            "approvalRequiredBeforeDeployment": True,
        },
        "safety": _phase26f_safety(),
    }


@router.get("/approval-gate/status")
def approval_gate_status():
    return {
        "ok": True,
        "phase": PHASE_26F,
        "service": SERVICE_NAME,
        "mode": "approval-gate-status",
        "approvalGateEnabled": True,
        "rules": {
            "product_plan": "Allowed without code/export/deployment.",
            "preview_generation": "Requires productPlanApproved.",
            "code_generation": "Requires productPlanApproved, previewApproved, codeGenerationApproved, and explicit userConfirmation.",
            "export_generation": "Requires productPlanApproved, previewApproved, exportApproved, and explicit userConfirmation.",
            "deployment": "Requires productPlanApproved, previewApproved, codeGenerationApproved, deploymentApproved, and explicit userConfirmation.",
        },
        "disabledInThisPhase": [
            "actual_code_generation",
            "file_writes_for_generated_apps",
            "export_generation",
            "deployment",
            "database",
            "auth",
            "upload_processing",
            "ocr",
            "image_analysis",
            "voice_transcription",
        ],
        "safety": _phase26f_safety(),
    }
