from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, *, action: str, actor_hash: str, case_id: str | None = None, status: str = "ok", detail: dict[str, Any] | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "actor_hash": actor_hash,
            "case_id": case_id,
            "status": status,
            "detail": detail or {},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
