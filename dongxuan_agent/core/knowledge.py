from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


DEFAULT_KNOWLEDGE_ROOT = Path("/home/source/Documents/东玄知识库/wiki")


@dataclass(frozen=True)
class KnowledgeLocation:
    root: Path
    status: Literal["available", "missing", "unreadable"]
    source: Literal["environment", "default"]


def resolve_knowledge_location() -> KnowledgeLocation:
    configured = os.getenv("DONGXUAN_KNOWLEDGE_ROOT")
    root = Path(configured).expanduser() if configured else DEFAULT_KNOWLEDGE_ROOT
    source: Literal["environment", "default"] = "environment" if configured else "default"
    if not root.exists():
        return KnowledgeLocation(root, "missing", source)
    if not root.is_dir() or not os.access(root, os.R_OK):
        return KnowledgeLocation(root, "unreadable", source)
    return KnowledgeLocation(root, "available", source)


def relative_source(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_knowledge_json(path: Path) -> tuple[dict, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, "missing"
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}, "invalid"
    return (payload, "available") if isinstance(payload, dict) else ({}, "invalid")
