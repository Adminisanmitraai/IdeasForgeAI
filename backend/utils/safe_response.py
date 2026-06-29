import os


PHASE_26A = "26A"
PHASE_26B = "26B"
PHASE_26D = "26D"
PHASE_26E = "26E"
PHASE_26F = "26F"
PHASE_27A = "27A"
PHASE_27B = "27B"
PHASE_27C = "27C"
SERVICE_NAME = "ideasforgeai-backend"
CONTRACT_VERSION = "2026-06-29-phase-27c"

DISABLED_CAPABILITIES = [
    "code_generation",
    "database",
    "auth",
    "billing",
    "file_upload_processing",
    "ocr",
    "image_analysis",
    "voice_transcription",
    "deployment",
]


def is_openai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


def safety_flags() -> dict:
    return {
        "openaiConnected": is_openai_configured(),
        "databaseConnected": False,
        "fileProcessingEnabled": False,
        "voiceEnabled": False,
        "deploymentEnabled": False,
        "sectorClassificationEnabled": True,
        "requirementExpansionEnabled": True,
        "workflowMappingEnabled": True,
        "productGenerationEnabled": True,
        "previewGenerationEnabled": True,
        "approvalGateEnabled": True,
        "codeGenerationEnabled": False,
    }


def validation_error(message: str, code: str = "VALIDATION_ERROR") -> dict:
    return {
        "ok": False,
        "phase": PHASE_27C,
        "error": {
            "code": code,
            "message": message,
        },
        "safety": safety_flags(),
    }


def disabled_capability_report() -> dict:
    return {
        "openaiConnected": is_openai_configured(),
        "databaseConnected": False,
        "fileProcessingEnabled": False,
        "deploymentEnabled": False,
        "sectorClassificationEnabled": True,
        "requirementExpansionEnabled": True,
        "workflowMappingEnabled": True,
        "productGenerationEnabled": True,
        "previewGenerationEnabled": True,
        "approvalGateEnabled": True,
        "codeGenerationEnabled": False,
    }
