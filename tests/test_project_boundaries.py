from pathlib import Path
import tomllib


def test_web_and_docker_features_are_removed():
    assert not Path("dongxuan_agent/web").exists()
    assert not Path("Dockerfile").exists()
    assert not Path("docker-compose.yml").exists()
    assert not Path("scripts/start-readonly-web.sh").exists()


def test_runtime_dependencies_only_contain_domain_engine():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["dependencies"] == ["sxtwl"]
