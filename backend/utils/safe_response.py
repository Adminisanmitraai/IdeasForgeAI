PHASE_26A = "26A"
SERVICE_NAME = "ideasforgeai-backend"
CONTRACT_VERSION = "2026-06-29-phase-26a"

DISABLED_CAPABILITIES = [
    "openai_chat",
    "product_generation",
    "database",
    "auth",
    "billing",
    "file_upload_processing",
    "ocr",
    "image_analysis",
    "voice_transcription",
    "deployment",
]

SAFETY_FLAGS = {
    "openaiConnected": False,
    "databaseConnected": False,
    "fileProcessingEnabled": False,
    "voiceEnabled": False,
    "deploymentEnabled": False,
}


def validation_error(message: str, code: str = "VALIDATION_ERROR") -> dict:
    return {
        "ok": False,
        "phase": PHASE_26A,
        "error": {
            "code": code,
            "message": message,
        },
    }


def disabled_capability_report() -> dict:
    return {
        "openaiConnected": False,
        "databaseConnected": False,
        "fileProcessingEnabled": False,
        "deploymentEnabled": False,
    }
