from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "IdeasForgeAI Backend",
        "message": "IdeasForgeAI backend is running.",
    }