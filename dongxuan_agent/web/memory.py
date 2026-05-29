from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CaseStore:
    def __init__(self, path: Path, *, max_records: int = 20) -> None:
        self.path = path
        self.max_records = max_records

    def list_cases(self) -> list[dict[str, Any]]:
        data = self._read()
        return data["cases"]

    def get_case(self, case_id: str) -> dict[str, Any]:
        case = self._find_case(case_id)
        return deepcopy(case)

    def create_case(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        now = _now()
        case = _normalize_case(
            {
                "id": f"case_{uuid.uuid4().hex}",
                "title": payload.get("title") or "新的案例",
                "system": payload.get("system") or "bazi",
                "created_at": now,
                "updated_at": now,
                **payload,
            }
        )
        data["cases"].insert(0, case)
        self._write(data)
        return deepcopy(case)

    def update_case(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        case = _find_in_data(data, case_id)
        for key in ("title", "birth", "bazi", "luck", "background", "facts", "intents", "notes"):
            if key in payload:
                case[key] = payload[key]
        case["updated_at"] = _now()
        normalized = _normalize_case(case)
        case.clear()
        case.update(normalized)
        self._write(data)
        return deepcopy(case)

    def delete_case(self, case_id: str) -> None:
        data = self._read()
        data["cases"] = [case for case in data["cases"] if case.get("id") != case_id]
        self._write(data)

    def append_record(self, case_id: str, *, question: str | None, analysis: str, conclusion: str, context: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        case = _find_in_data(data, case_id)
        records = list(case.get("records") or [])
        records.append(
            {
                "id": f"record_{uuid.uuid4().hex}",
                "created_at": _now(),
                "question": question or "",
                "analysis": analysis,
                "conclusion": conclusion,
                "context": context,
            }
        )
        case["records"] = records[-self.max_records :]
        case["updated_at"] = _now()
        normalized = _normalize_case(case)
        case.clear()
        case.update(normalized)
        self._write(data)
        return deepcopy(case)

    def merge_chart_snapshot(self, case_id: str, context: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        case = _find_in_data(data, case_id)
        case["bazi"] = {
            "calendar": context.get("calendar", {}),
            "day_master": context.get("day_master"),
            "pillars": context.get("pillars", []),
        }
        case["luck"] = context.get("luck") or {}
        notes = _dict(case.get("notes"))
        if context.get("analysis_hints"):
            year = str(context["analysis_hints"].get("target_year"))
            notes.setdefault("year_hints", {})[year] = context["analysis_hints"]
        if context.get("luck_year_remedy"):
            year = str((context.get("analysis_hints") or {}).get("target_year", "unknown"))
            notes.setdefault("luck_year_remedy", {})[year] = context["luck_year_remedy"]
        case["notes"] = notes
        case["updated_at"] = _now()
        normalized = _normalize_case(case)
        case.clear()
        case.update(normalized)
        self._write(data)
        return deepcopy(case)

    def _find_case(self, case_id: str) -> dict[str, Any]:
        return _find_in_data(self._read(), case_id)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "cases": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "cases": []}
        if not isinstance(data, dict):
            return {"version": 1, "cases": []}
        cases = data.get("cases")
        return {"version": 1, "cases": cases if isinstance(cases, list) else []}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, self.path)


def _find_in_data(data: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in data["cases"]:
        if case.get("id") == case_id:
            return case
    raise KeyError(case_id)


def _normalize_case(case: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "id": str(case.get("id") or f"case_{uuid.uuid4().hex}"),
        "title": str(case.get("title") or "新的案例"),
        "system": str(case.get("system") or "bazi"),
        "created_at": str(case.get("created_at") or _now()),
        "updated_at": str(case.get("updated_at") or _now()),
        "birth": _dict(case.get("birth")),
        "bazi": _dict(case.get("bazi")),
        "luck": _dict(case.get("luck")),
        "background": str(case.get("background") or ""),
        "facts": [_normalize_fact(item) for item in _list(case.get("facts"))],
        "intents": [_normalize_intent(item) for item in _list(case.get("intents"))],
        "notes": _dict(case.get("notes")),
        "records": _list(case.get("records")),
    }
    normalized["notes"].setdefault("summary", "")
    return normalized


def _normalize_fact(item: Any) -> dict[str, Any]:
    raw = _dict(item)
    return {
        "id": str(raw.get("id") or f"fact_{uuid.uuid4().hex}"),
        "text": str(raw.get("text") or ""),
        "source": str(raw.get("source") or "user_verified"),
        "confidence": str(raw.get("confidence") or "verified"),
        "created_at": str(raw.get("created_at") or _now()),
    }


def _normalize_intent(item: Any) -> dict[str, Any]:
    raw = _dict(item)
    return {
        "id": str(raw.get("id") or f"intent_{uuid.uuid4().hex}"),
        "text": str(raw.get("text") or ""),
        "status": str(raw.get("status") or "pending"),
        "created_at": str(raw.get("created_at") or _now()),
    }


def _dict(value: Any) -> dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
