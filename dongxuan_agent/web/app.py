from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .config import WebSettings, load_settings
from .llm import LLMAdapter, build_llm_adapter
from .services import analyze_bazi, analyze_daliuren

STATIC_DIR = Path(__file__).with_name("static")


class PasswordPayload(BaseModel):
    password: str | None = None


class BaziAnalyzeRequest(PasswordPayload):
    datetime: str = Field(default="2006-12-18 12:30:00")
    timezone: str = Field(default="Asia/Shanghai")
    gender: Literal["男", "女"] | None = None
    longitude: float | None = None
    zi_hour_rule: Literal["whole", "split"] = "whole"
    target_year: int | None = None
    question: str | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str | None) -> str | None:
        return _validate_question_length(value)


class DaliurenAnalyzeRequest(PasswordPayload):
    datetime: str = Field(default="2026-05-28 20:00:00")
    timezone: str = Field(default="Asia/Shanghai")
    mode: Literal["time", "live-hour", "number"] = "time"
    hour_branch: str | None = None
    number: int | None = None
    gender: Literal["男", "女"] | None = None
    question: str | None = None
    background: str | None = None
    birth_year: int | None = None

    @field_validator("question", "background")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _validate_question_length(value)


def create_app() -> FastAPI:
    settings = load_settings()
    adapter = build_llm_adapter(settings)
    app = FastAPI(title="Dongxuan Readonly Web", version="0.1.0")

    app.state.settings = settings
    app.state.llm_adapter = adapter

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "systems": ["bazi", "daliuren"], "readonly": True}

    @app.post("/api/bazi/analyze")
    def bazi_analyze(request: BaziAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter] = Depends(_deps)) -> dict:
        active_settings, active_adapter = deps
        _require_password(request.password, active_settings)
        return _run_analysis(lambda: analyze_bazi(request, active_adapter))

    @app.post("/api/daliuren/analyze")
    def daliuren_analyze(request: DaliurenAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter] = Depends(_deps)) -> dict:
        active_settings, active_adapter = deps
        _require_password(request.password, active_settings)
        return _run_analysis(lambda: analyze_daliuren(request, active_adapter))

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-store"})

    return app


def _deps() -> tuple[WebSettings, LLMAdapter]:
    settings = load_settings()
    return settings, build_llm_adapter(settings)


def _require_password(password: str | None, settings: WebSettings) -> None:
    if settings.access_password and password != settings.access_password:
        raise HTTPException(status_code=401, detail="Invalid access password")


def _run_analysis(callback):
    try:
        return callback()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def _validate_question_length(value: str | None) -> str | None:
    if value is not None and len(value) > load_settings().max_question_length:
        raise ValueError("text is too long")
    return value


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("dongxuan_agent.web.app:app", host="0.0.0.0", port=8000)
