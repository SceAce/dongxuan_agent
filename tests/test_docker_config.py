from pathlib import Path


def test_docker_compose_mounts_writable_memory_volume():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "DONGXUAN_MEMORY_PATH" in compose
    assert "/data/dongxuan/memory.json" in compose
    assert "./dongxuan-data:/data/dongxuan" in compose
    assert "read_only: true" in compose


def test_dockerfile_defaults_to_persistent_memory_path():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "DONGXUAN_MEMORY_PATH=/data/dongxuan/memory.json" in dockerfile
    assert "EXPOSE 8000" in dockerfile
