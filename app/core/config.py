import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv


load_dotenv()


Provider = Literal["openai", "groq"]


@dataclass(frozen=True)
class Settings:
    provider: Provider
    api_key: str
    base_url: str
    model: str
    timeout_seconds: float


def get_settings() -> Settings:
    provider_raw = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    if provider_raw not in {"openai", "groq"}:
        raise ValueError("LLM_PROVIDER must be 'openai' or 'groq'.")

    provider: Provider = provider_raw  # type: ignore[assignment]
    timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY for provider 'openai'.")

        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    else:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY for provider 'groq'.")

        base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

    if not model:
        raise ValueError("Model value cannot be empty.")

    return Settings(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout_seconds=timeout_seconds,
    )
