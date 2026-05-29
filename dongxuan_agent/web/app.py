from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .config import WebSettings, load_settings
from .llm import LLMAdapter, build_llm_adapter
from .memory import CaseStore
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


class CasePayload(PasswordPayload):
    title: str | None = None
    system: Literal["bazi", "daliuren"] = "bazi"
    birth: dict = Field(default_factory=dict)
    bazi: dict = Field(default_factory=dict)
    luck: dict = Field(default_factory=dict)
    background: str = ""
    facts: list[dict] = Field(default_factory=list)
    intents: list[dict] = Field(default_factory=list)
    notes: dict = Field(default_factory=dict)


class CasePatchPayload(PasswordPayload):
    title: str | None = None
    birth: dict | None = None
    bazi: dict | None = None
    luck: dict | None = None
    background: str | None = None
    facts: list[dict] | None = None
    intents: list[dict] | None = None
    notes: dict | None = None


def create_app() -> FastAPI:
    settings = load_settings()
    adapter = build_llm_adapter(settings)
    case_store = CaseStore(settings.memory_path)
    app = FastAPI(title="Dongxuan Readonly Web", version="0.1.0")

    app.state.settings = settings
    app.state.llm_adapter = adapter
    app.state.case_store = case_store

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

    @app.get("/api/cases")
    def list_cases(deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> list[dict]:
        _, _, active_store = deps
        return active_store.list_cases()

    @app.post("/api/cases")
    def create_case(request: CasePayload, deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> dict:
        active_settings, _, active_store = deps
        _require_password(request.password, active_settings)
        return active_store.create_case(request.model_dump(exclude={"password"}))

    @app.get("/api/cases/{case_id}")
    def get_case(case_id: str, deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> dict:
        _, _, active_store = deps
        return _case_or_404(lambda: active_store.get_case(case_id))

    @app.patch("/api/cases/{case_id}")
    def update_case(case_id: str, request: CasePatchPayload, deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> dict:
        active_settings, _, active_store = deps
        _require_password(request.password, active_settings)
        payload = request.model_dump(exclude={"password"}, exclude_none=True)
        return _case_or_404(lambda: active_store.update_case(case_id, payload))

    @app.delete("/api/cases/{case_id}")
    def delete_case(case_id: str, request: PasswordPayload | None = None, deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> dict:
        active_settings, _, active_store = deps
        _require_password(request.password if request else None, active_settings)
        active_store.delete_case(case_id)
        return {"deleted": True}

    @app.post("/api/cases/{case_id}/bazi/analyze")
    def analyze_case_bazi(case_id: str, request: BaziAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter, CaseStore] = Depends(_deps_with_store)) -> dict:
        active_settings, active_adapter, active_store = deps
        _require_password(request.password, active_settings)
        case = _case_or_404(lambda: active_store.get_case(case_id))
        result = _run_analysis(lambda: analyze_bazi(request, active_adapter, _case_memory(case)))
        conclusion = _extract_conclusion(result["analysis"])
        active_store.append_record(
            case_id,
            question=request.question,
            analysis=result["analysis"],
            conclusion=conclusion,
            context=result["context"],
        )
        return result

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-store"})

    return app


def _deps() -> tuple[WebSettings, LLMAdapter]:
    settings = load_settings()
    return settings, build_llm_adapter(settings)


def _deps_with_store() -> tuple[WebSettings, LLMAdapter, CaseStore]:
    settings = load_settings()
    return settings, build_llm_adapter(settings), CaseStore(settings.memory_path)


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


def _case_or_404(callback):
    try:
        return callback()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc


def _case_memory(case: dict) -> dict:
    return {
        "title": case.get("title", ""),
        "birth": case.get("birth", {}),
        "bazi": case.get("bazi", {}),
        "luck": case.get("luck", {}),
        "background": case.get("background", ""),
        "facts": case.get("facts", []),
        "intents": case.get("intents", []),
        "summary": case.get("notes", {}).get("summary", ""),
        "recent_records": [
            {
                "question": record.get("question", ""),
                "conclusion": record.get("conclusion", ""),
            }
            for record in case.get("records", [])[-5:]
        ],
    }


def _extract_conclusion(analysis: str) -> str:
    marker = "## 结论"
    if marker in analysis:
        return analysis.split(marker, 1)[1].strip()
    return analysis.strip()


def _validate_question_length(value: str | None) -> str | None:
    if value is not None and len(value) > load_settings().max_question_length:
        raise ValueError("text is too long")
    return value


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("dongxuan_agent.web.app:app", host="0.0.0.0", port=8000)
