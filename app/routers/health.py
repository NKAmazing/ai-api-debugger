from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Simple endpoint to verify API availability.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="ai-api-debugger")
