from fastapi import APIRouter, HTTPException, status

from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisResponse
from app.services.llm_analyzer import (
    LLMAPIError,
    LLMInvalidResponseError,
    analyze_api_error,
)


router = APIRouter()


@router.post(
    "/analyze-error",
    response_model=ErrorAnalysisResponse,
    summary="Analyze API errors and return debugging insights",
)
async def analyze_error(payload: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    try:
        return await analyze_api_error(payload)
    except LLMInvalidResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "InvalidLLMResponse",
                "message": str(exc),
            },
        ) from exc
    except LLMAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLMServiceUnavailable",
                "message": str(exc),
            },
        ) from exc
