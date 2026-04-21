import json

from openai import APIError, AsyncOpenAI
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.error_analysis import ErrorAnalysisRequest, ErrorAnalysisResponse


SYSTEM_PROMPT = """
You are an expert API debugging assistant.
You analyze API failures and return concise, actionable diagnostics.
Respond ONLY with valid JSON with this exact schema:
{
  "diagnosis": "string",
  "possible_causes": ["string"],
  "suggested_fix": "string"
}
Do not include markdown, code fences, comments, or extra keys.
""".strip()


class LLMInvalidResponseError(Exception):
    """Raised when the LLM output is not valid JSON for expected schema."""


class LLMAPIError(Exception):
    """Raised when upstream LLM call fails."""


def _build_client(api_key: str, base_url: str, timeout_seconds: float) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout_seconds,
    )


def _build_user_prompt(payload: ErrorAnalysisRequest) -> str:
    return json.dumps(
        {
            "api_url": payload.api_url,
            "method": payload.method,
            "status_code": payload.status_code,
            "error_message": payload.error_message,
            "context": payload.context,
        },
        ensure_ascii=True,
    )


async def analyze_api_error(payload: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    try:
        settings = get_settings()
    except ValueError as exc:
        raise LLMAPIError(str(exc)) from exc

    client = _build_client(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout_seconds=settings.timeout_seconds,
    )

    try:
        completion = await client.chat.completions.create(
            model=settings.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(payload)},
            ],
            temperature=0.2,
        )
    except APIError as exc:
        raise LLMAPIError(f"LLM API request failed: {exc}") from exc
    except Exception as exc:
        raise LLMAPIError(f"Unexpected LLM failure: {exc}") from exc

    try:
        raw_content = completion.choices[0].message.content
    except (IndexError, AttributeError, TypeError) as exc:
        raise LLMInvalidResponseError("LLM response did not contain message content.") from exc

    if not raw_content:
        raise LLMInvalidResponseError("LLM response content is empty.")

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise LLMInvalidResponseError("LLM returned invalid JSON.") from exc

    try:
        return ErrorAnalysisResponse.model_validate(parsed)
    except ValidationError as exc:
        raise LLMInvalidResponseError(
            f"LLM JSON does not match required schema: {exc.errors()}"
        ) from exc
