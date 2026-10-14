from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_knowledge_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "missing-knowledge"
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    return root


@pytest.fixture
def available_knowledge_root(
    isolated_knowledge_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    root = tmp_path / "wiki"
    structured = root / "structured"
    entities = root / "entities"
    structured.mkdir(parents=True)
    entities.mkdir(parents=True)

    payload = json.loads(
        (Path(__file__).parent / "fixtures" / "bazi_symbolic_layers.json").read_text(encoding="utf-8")
    )
    (structured / "bazi_symbolic_layers.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    for term in ("五行", "十神", "旺衰", "干支"):
        (entities / f"{term}.md").write_text(
            f"# {term}\n\n这是测试用的最小知识条目。",
            encoding="utf-8",
        )

    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    return root
