from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class ErrorAnalysisRequest(BaseModel):
    api_url: HttpUrl = Field(..., description="URL of the API endpoint that failed.")
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        ..., description="HTTP method used for the failed request."
    )
    status_code: int = Field(
        ...,
        ge=100,
        le=599,
        description="HTTP status code returned by the API.",
    )
    error_message: str = Field(..., min_length=1, description="Raw API error message.")
    context: Optional[str] = Field(
        default=None,
        description="Optional additional debugging context.",
    )


class ErrorAnalysisResponse(BaseModel):
    diagnosis: str = Field(..., min_length=1)
    possible_causes: list[str] = Field(..., min_length=1)
    suggested_fix: str = Field(..., min_length=1)
