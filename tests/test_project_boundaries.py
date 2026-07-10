import tomllib
from pathlib import Path


def test_web_and_docker_features_are_removed():
    assert not Path("dongxuan_agent/web").exists()
    assert not Path("Dockerfile").exists()
    assert not Path("docker-compose.yml").exists()
    assert not Path("scripts/start-readonly-web.sh").exists()
    assert not Path("docs/superpowers/plans/2026-05-28-readonly-web-mvp.md").exists()
    assert not Path("docs/superpowers/specs/2026-05-28-readonly-web-mvp-design.md").exists()


def test_runtime_dependencies_only_contain_domain_engine():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["dependencies"] == ["sxtwl"]
