from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WebSettings:
    access_password: str | None
    llm_provider: str
    openai_api_key: str | None
    openai_base_url: str
    openai_model: str
    request_timeout_seconds: float
    max_question_length: int


def load_settings() -> WebSettings:
    codex_auth = _load_codex_auth()
    return WebSettings(
        access_password=_blank_to_none(os.getenv("DONGXUAN_ACCESS_PASSWORD")),
        llm_provider=os.getenv("DONGXUAN_LLM_PROVIDER", "echo").strip().lower() or "echo",
        openai_api_key=_blank_to_none(os.getenv("OPENAI_API_KEY")) or _blank_to_none(_auth_value(codex_auth, "OPENAI_API_KEY", "api_key", "openai_api_key")),
        openai_base_url=(
            _blank_to_none(os.getenv("OPENAI_BASE_URL"))
            or _blank_to_none(_auth_value(codex_auth, "OPENAI_BASE_URL", "base_url", "openai_base_url"))
            or "https://api.openai.com/v1"
        ),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
        request_timeout_seconds=float(os.getenv("DONGXUAN_REQUEST_TIMEOUT_SECONDS", "60")),
        max_question_length=int(os.getenv("DONGXUAN_MAX_QUESTION_LENGTH", "2000")),
    )


def _load_codex_auth() -> dict:
    for path in _candidate_auth_paths():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        return data if isinstance(data, dict) else {}
    return {}


def _candidate_auth_paths() -> list[Path]:
    explicit = _blank_to_none(os.getenv("DONGXUAN_CODEX_AUTH_PATH"))
    if explicit:
        return [Path(explicit).expanduser()]
    codex_dir = Path.home() / ".codex"
    return [
        codex_dir / "atuo.json",
        codex_dir / "auto.json",
        codex_dir / "auth.json",
    ]


def _auth_value(data: dict, *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str):
            return value
    return None


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
