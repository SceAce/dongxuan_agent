from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class WebSettings:
    access_password: str | None
    llm_provider: str
    openai_api_key: str | None
    openai_model: str
    request_timeout_seconds: float
    max_question_length: int


def load_settings() -> WebSettings:
    return WebSettings(
        access_password=_blank_to_none(os.getenv("DONGXUAN_ACCESS_PASSWORD")),
        llm_provider=os.getenv("DONGXUAN_LLM_PROVIDER", "echo").strip().lower() or "echo",
        openai_api_key=_blank_to_none(os.getenv("OPENAI_API_KEY")),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
        request_timeout_seconds=float(os.getenv("DONGXUAN_REQUEST_TIMEOUT_SECONDS", "60")),
        max_question_length=int(os.getenv("DONGXUAN_MAX_QUESTION_LENGTH", "2000")),
    )


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
