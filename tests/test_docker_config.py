from pathlib import Path


def test_docker_compose_mounts_writable_memory_volume():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert 'DONGXUAN_LLM_PROVIDER: "${DONGXUAN_LLM_PROVIDER:-openai}"' in compose
    assert "DONGXUAN_MEMORY_PATH" in compose
    assert "DONGXUAN_AUDIT_LOG_PATH" in compose
    assert "/data/dongxuan/memory.json" in compose
    assert "/data/dongxuan/audit.jsonl" in compose
    assert "./dongxuan-data:/data/dongxuan" in compose
    assert "read_only: true" in compose


def test_dockerfile_defaults_to_persistent_memory_path():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "DONGXUAN_LLM_PROVIDER=openai" in dockerfile
    assert "DONGXUAN_MEMORY_PATH=/data/dongxuan/memory.json" in dockerfile
    assert "EXPOSE 8000" in dockerfile


def test_env_example_documents_openai_compatible_settings():
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "DONGXUAN_LLM_PROVIDER=openai" in env_example
    assert "DONGXUAN_AUDIT_LOG_PATH=/data/dongxuan/audit.jsonl" in env_example
    assert "OPENAI_API_KEY=" in env_example
    assert "OPENAI_BASE_URL=https://aivalux.com" in env_example
    assert "OPENAI_MODEL=" in env_example
    assert "OPENAI_WIRE_API=responses" in env_example
