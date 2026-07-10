from importlib import import_module, util


def _knowledge_module():
    assert util.find_spec("dongxuan_agent.core.knowledge") is not None
    return import_module("dongxuan_agent.core.knowledge")


def test_knowledge_root_prefers_environment(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    root.mkdir()
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))

    location = _knowledge_module().resolve_knowledge_location()

    assert location.root == root
    assert location.status == "available"
    assert location.source == "environment"


def test_missing_knowledge_root_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(tmp_path / "missing"))

    location = _knowledge_module().resolve_knowledge_location()

    assert location.status == "missing"
    assert location.source == "environment"


def test_relative_source_never_exposes_root(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    page = root / "topics" / "八字.md"
    page.parent.mkdir(parents=True)
    page.write_text("# 八字", encoding="utf-8")
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))

    module = _knowledge_module()
    location = module.resolve_knowledge_location()

    assert module.relative_source(page, location.root) == "topics/八字.md"


def test_invalid_knowledge_json_degrades_explicitly(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    path = root / "structured" / "broken.json"
    path.parent.mkdir(parents=True)
    path.write_text("{broken", encoding="utf-8")
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))

    payload, status = _knowledge_module().read_knowledge_json(path)

    assert payload == {}
    assert status == "invalid"
