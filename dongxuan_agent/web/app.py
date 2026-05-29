from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .audit import AuditLogger
from .config import WebSettings, load_settings
from .llm import LLMAdapter, build_llm_adapter
from .memory import CaseStore
from .services import analyze_bazi, analyze_daliuren

STATIC_DIR = Path(__file__).with_name("static")


class PasswordPayload(BaseModel):
    password: str | None = None


@dataclass(frozen=True)
class Actor:
    password: str
    owner_hash: str
    is_admin: bool = False


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
    app.state.audit_logger = AuditLogger(settings.audit_log_path)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "systems": ["bazi", "daliuren"], "readonly": True}

    @app.post("/api/bazi/analyze")
    def bazi_analyze(request: BaziAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, active_adapter, _, _ = deps
        actor = _require_actor(request.password, active_settings)
        _audit(deps, "bazi.analyze", actor)
        return _run_analysis(lambda: analyze_bazi(request, active_adapter))

    @app.post("/api/daliuren/analyze")
    def daliuren_analyze(request: DaliurenAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, active_adapter, _, _ = deps
        actor = _require_actor(request.password, active_settings)
        _audit(deps, "daliuren.analyze", actor)
        return _run_analysis(lambda: analyze_daliuren(request, active_adapter))

    @app.get("/api/cases")
    def list_cases_requires_password() -> list[dict]:
        raise HTTPException(status_code=401, detail=_password_required_message())

    @app.post("/api/cases/list")
    def list_cases(request: PasswordPayload, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> list[dict]:
        active_settings, _, active_store, _ = deps
        actor = _require_actor(request.password, active_settings)
        _audit(deps, "case.list", actor)
        return active_store.list_cases(owner_hash=actor.owner_hash, include_all=actor.is_admin)

    @app.post("/api/cases")
    def create_case(request: CasePayload, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, _, active_store, _ = deps
        actor = _require_actor(request.password, active_settings)
        created = active_store.create_case(request.model_dump(exclude={"password"}), owner_hash=actor.owner_hash)
        _audit(deps, "case.create", actor, case_id=created["id"])
        return created

    @app.get("/api/cases/{case_id}")
    def get_case_requires_password(case_id: str) -> dict:
        raise HTTPException(status_code=401, detail=_password_required_message())

    @app.post("/api/cases/{case_id}/get")
    def get_case(case_id: str, request: PasswordPayload, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, _, active_store, _ = deps
        actor = _require_actor(request.password, active_settings)
        case = _case_or_404(lambda: active_store.get_case(case_id, owner_hash=actor.owner_hash, include_all=actor.is_admin))
        _audit(deps, "case.get", actor, case_id=case_id)
        return case

    @app.patch("/api/cases/{case_id}")
    def update_case(case_id: str, request: CasePatchPayload, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, _, active_store, _ = deps
        actor = _require_actor(request.password, active_settings)
        payload = request.model_dump(exclude={"password"}, exclude_none=True)
        updated = _case_or_404(lambda: active_store.update_case(case_id, payload, owner_hash=actor.owner_hash, include_all=actor.is_admin))
        _audit(deps, "case.update", actor, case_id=case_id)
        return updated

    @app.delete("/api/cases/{case_id}")
    def delete_case(case_id: str, request: PasswordPayload | None = None, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, _, active_store, _ = deps
        actor = _require_actor(request.password if request else None, active_settings)
        active_store.delete_case(case_id, owner_hash=actor.owner_hash, include_all=actor.is_admin)
        _audit(deps, "case.delete", actor, case_id=case_id)
        return {"deleted": True}

    @app.post("/api/cases/{case_id}/bazi/analyze")
    def analyze_case_bazi(case_id: str, request: BaziAnalyzeRequest, deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger] = Depends(_deps_full)) -> dict:
        active_settings, active_adapter, active_store, _ = deps
        actor = _require_actor(request.password, active_settings)
        case = _case_or_404(lambda: active_store.get_case(case_id, owner_hash=actor.owner_hash, include_all=actor.is_admin))
        active_request = _with_inferred_target_year(request)
        result = _run_analysis(lambda: analyze_bazi(active_request, active_adapter, _case_memory(case)))
        conclusion = _extract_conclusion(result["analysis"])
        active_store.merge_chart_snapshot(case_id, result["context"], owner_hash=actor.owner_hash, include_all=actor.is_admin)
        active_store.append_record(
            case_id,
            question=active_request.question,
            analysis=result["analysis"],
            conclusion=conclusion,
            context=result["context"],
            owner_hash=actor.owner_hash,
            include_all=actor.is_admin,
        )
        _audit(deps, "case.bazi.analyze", actor, case_id=case_id)
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


def _deps_full() -> tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger]:
    settings = load_settings()
    return settings, build_llm_adapter(settings), CaseStore(settings.memory_path), AuditLogger(settings.audit_log_path)


def _require_actor(password: str | None, settings: WebSettings) -> Actor:
    del settings
    clean = (password or "").strip()
    if not clean:
        raise HTTPException(status_code=401, detail=_password_required_message())
    return Actor(password=clean, owner_hash=_password_fingerprint(clean), is_admin=clean == "sudo")


def _password_required_message() -> str:
    return "请输入访问密码。如果第一次使用，请在密码框里设置一个自己的密码；之后使用同一个密码即可看到自己的对话。管理员密码 sudo 可查看全部。"


def _password_fingerprint(password: str) -> str:
    return hashlib.sha256(f"dongxuan-web:{password}".encode("utf-8")).hexdigest()


def _audit(deps: tuple[WebSettings, LLMAdapter, CaseStore, AuditLogger], action: str, actor: Actor, *, case_id: str | None = None, status: str = "ok") -> None:
    _, _, _, logger = deps
    logger.write(action=action, actor_hash=actor.owner_hash, case_id=case_id, status=status, detail={"admin": actor.is_admin})


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


def _with_inferred_target_year(request: BaziAnalyzeRequest) -> BaziAnalyzeRequest:
    if request.target_year is not None:
        return request
    inferred = _infer_target_year(request.question)
    if inferred is None:
        return request
    payload = request.model_dump()
    payload["target_year"] = inferred
    return BaziAnalyzeRequest(**payload)


def _infer_target_year(question: str | None) -> int | None:
    if not question:
        return None
    years = [int(match) for match in re.findall(r"(?<!\d)(19\d{2}|20\d{2}|21\d{2})(?=年?)(?!\d)", question)]
    if not years:
        return None
    return years[-1]


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
