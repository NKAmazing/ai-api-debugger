# AI API Debugger

A FastAPI API that receives real API error data and uses an LLM to return a structured diagnosis with likely causes and suggested fixes.

## Stack

- `fastapi`: async web framework
- `uvicorn`: ASGI server
- `httpx`: useful dependency for async HTTP ecosystem work
- `python-dotenv`: environment variable loading
- `openai`: OpenAI-compatible client (works with OpenAI, Groq, and other compatible providers)
- `pydantic` (included by FastAPI): strict input/output validation

## Architecture

```text
app/
  main.py                 # FastAPI app + router wiring + validation handler
  core/
    config.py             # Centralized environment configuration
  routers/
    health.py             # Health check endpoint (/health)
    error_analysis.py     # HTTP endpoint (/analyze-error)
  services/
    llm_analyzer.py       # LLM logic and JSON parsing/validation
  schemas/
    error_analysis.py     # Request/response models (Pydantic)
```

Applied principle:
- Routers only orchestrate HTTP concerns.
- Services contain business/LLM logic.
- Schemas define input/output contracts.

## Configuration

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
cp .env.example .env
```

Variables:
- `LLM_PROVIDER`: `openai` or `groq`
- `LLM_TIMEOUT_SECONDS`: LLM call timeout
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`
- `GROQ_API_KEY`, `GROQ_BASE_URL`, `GROQ_MODEL`

### Option 1: OpenAI + GPT

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### Option 2: Groq (free tier) + open-source model

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant
```

## Recommended free / low-cost models

The app uses an OpenAI-compatible client and selects the provider from `app/core/config.py`, so you can switch between OpenAI and Groq by changing only environment variables.

Common options:
- Groq (often has a free tier): `GROQ_BASE_URL=https://api.groq.com/openai/v1`
- OpenRouter (depends on model and plan)
- OpenAI (usually requires billing)

## Run

```bash
uvicorn app.main:app --reload
```

Swagger UI:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

### `GET /health`

Response body:

```json
{
  "status": "ok",
  "service": "ai-api-debugger"
}
```

### `POST /analyze-error`

Request body:

```json
{
  "api_url": "https://api.example.com/v1/users",
  "method": "GET",
  "status_code": 401,
  "error_message": "Invalid OAuth token",
  "context": "Token generated 2 hours ago with read scope only"
}
```

Response body:

```json
{
  "diagnosis": "OAuth token is invalid or expired for this endpoint.",
  "possible_causes": [
    "Access token expired",
    "Token audience does not match API",
    "Missing required OAuth scope"
  ],
  "suggested_fix": "Regenerate the token with correct audience and scopes, then retry with a valid Bearer token."
}
```

## LLM Integration Details

- A `system prompt` enforces API-debugging-expert behavior.
- JSON output is forced with `response_format={"type":"json_object"}`.
- Content is parsed with `json.loads`.
- Final output is validated with `ErrorAnalysisResponse` (Pydantic), preventing invalid formats.

## Error Handling

Covered errors:
- Invalid HTTP payload -> `422 ValidationError`
- Invalid JSON returned by LLM -> `502 InvalidLLMResponse`
- LLM provider failure / timeout / missing API key -> `503 LLMServiceUnavailable`

Clean error example:

```json
{
  "detail": {
    "error": "InvalidLLMResponse",
    "message": "LLM returned invalid JSON."
  }
}
```

## Applied Code Quality

- End-to-end async/await implementation.
- Layer separation (router/service/schema).
- Request and response validation via Pydantic.
- Explicit handling of infrastructure and parsing exceptions.

## Internal Flow

1. Client sends API error data to `POST /analyze-error`.
2. Router validates input and delegates to the service.
3. Service builds a structured prompt and calls the LLM.
4. JSON is parsed and validated against schema.
5. API returns consistent, typed diagnostics.
