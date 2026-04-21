from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.error_analysis import router as error_analysis_router
from app.routers.health import router as health_router


app = FastAPI(
    title="AI API Debugger",
    description="Analyze API errors with an LLM and return structured debugging insights.",
    version="0.1.0",
)

app.include_router(error_analysis_router, tags=["Error Analysis"])
app.include_router(health_router, tags=["Health"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request payload.",
            "details": exc.errors(),
        },
    )
