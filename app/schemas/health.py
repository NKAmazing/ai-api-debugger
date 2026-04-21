from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status.")
    service: str = Field(..., description="Service identifier.")
