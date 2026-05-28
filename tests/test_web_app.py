import json

from dongxuan_agent.bazi.context import build_bazi_context
from dongxuan_agent.chart import build_chart
from dongxuan_agent.divination import build_divination
from dongxuan_agent.render import chart_to_json, divination_to_json
from dongxuan_agent.rule_cards import build_rule_context


def test_health_endpoint_lists_readonly_systems(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "systems": ["bazi", "daliuren"], "readonly": True}


def test_bazi_analyze_matches_terminal_context_builder(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    request = {
        "datetime": "2006-12-18 12:30:00",
        "timezone": "Asia/Shanghai",
        "gender": "男",
        "zi_hour_rule": "whole",
        "target_year": 2025,
        "question": "推断2025年发生了什么",
    }
    expected_context = build_bazi_context(
        request["datetime"],
        timezone=request["timezone"],
        gender=request["gender"],
        zi_hour_rule=request["zi_hour_rule"],
        target_year=request["target_year"],
        question=request["question"],
    )

    client = TestClient(create_app())
    response = client.post("/api/bazi/analyze", json=request)

    assert response.status_code == 200
    payload = response.json()
    assert payload["system"] == "bazi"
    assert payload["context"] == _json_roundtrip(expected_context)
    assert payload["meta"]["readonly"] is True
    assert payload["meta"]["prompt_file"] == "bazi_prompt.md"
    assert "echo provider" in payload["analysis"]


def test_daliuren_analyze_matches_terminal_context_builder(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    request = {
        "datetime": "2026-05-28 20:00:00",
        "timezone": "Asia/Shanghai",
        "mode": "number",
        "number": 7,
        "gender": "男",
        "question": "问工作进展",
        "background": "正在等通知",
        "birth_year": 2000,
    }
    divination = build_divination(
        request["datetime"],
        timezone=request["timezone"],
        mode=request["mode"],
        number=request["number"],
        gender=request["gender"],
        question=request["question"],
        background=request["background"],
        birth_year=request["birth_year"],
    )
    expected_context = divination_to_json(divination)
    expected_context["rule_cards"] = build_rule_context(request["question"])

    client = TestClient(create_app())
    response = client.post("/api/daliuren/analyze", json=request)

    assert response.status_code == 200
    payload = response.json()
    assert payload["system"] == "daliuren"
    assert payload["context"] == _json_roundtrip(expected_context)
    assert payload["meta"]["readonly"] is True
    assert payload["meta"]["prompt_file"] == "daliuren_prompt.md"
    assert "echo provider" in payload["analysis"]


def test_daliuren_time_mode_without_divination_matches_chart_session(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    request = {"datetime": "2026-05-28 20:00:00", "timezone": "Asia/Shanghai", "mode": "time"}
    expected_context = chart_to_json(build_chart(request["datetime"], timezone=request["timezone"]))
    expected_context["rule_cards"] = build_rule_context(None)

    client = TestClient(create_app())
    response = client.post("/api/daliuren/analyze", json=request)

    assert response.status_code == 200
    assert response.json()["context"] == _json_roundtrip(expected_context)


def test_password_is_required_when_configured(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_ACCESS_PASSWORD", "secret")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.post("/api/bazi/analyze", json={"datetime": "2006-12-18 12:30:00"})
    assert response.status_code == 401

    ok_response = client.post(
        "/api/bazi/analyze",
        json={"password": "secret", "datetime": "2006-12-18 12:30:00"},
    )
    assert ok_response.status_code == 200


def test_question_length_is_bounded(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.post(
        "/api/bazi/analyze",
        json={"datetime": "2006-12-18 12:30:00", "question": "问" * 2001},
    )

    assert response.status_code == 422


def test_no_shell_or_codex_endpoint_is_exposed(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())

    for path in ["/api/shell", "/api/codex", "/api/agent", "/api/write"]:
        assert client.post(path, json={}).status_code == 404


def test_model_errors_are_returned_as_json(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    import dongxuan_agent.web.app as web_app
    from fastapi.testclient import TestClient

    def broken_analyze_bazi(request, adapter):
        raise RuntimeError("模型接口返回 401，请检查 OPENAI_API_KEY")

    monkeypatch.setattr(web_app, "analyze_bazi", broken_analyze_bazi)

    client = TestClient(web_app.create_app())
    response = client.post("/api/bazi/analyze", json={"datetime": "2006-12-18 12:30:00"})

    assert response.status_code == 502
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"] == "模型接口返回 401，请检查 OPENAI_API_KEY"


def test_settings_can_read_openai_key_and_base_url_from_codex_auth_file(tmp_path, monkeypatch):
    auth_path = tmp_path / "auth.json"
    auth_path.write_text(
        '{"OPENAI_API_KEY": "sk-test-from-file", "OPENAI_BASE_URL": "https://example.test/v1"}',
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("DONGXUAN_CODEX_AUTH_PATH", str(auth_path))

    from dongxuan_agent.web.config import load_settings

    settings = load_settings()

    assert settings.openai_api_key == "sk-test-from-file"
    assert settings.openai_base_url == "https://example.test/v1"


def test_environment_openai_settings_override_codex_auth_file(tmp_path, monkeypatch):
    auth_path = tmp_path / "auth.json"
    auth_path.write_text(
        '{"OPENAI_API_KEY": "sk-test-from-file", "OPENAI_BASE_URL": "https://example.test/v1"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("DONGXUAN_CODEX_AUTH_PATH", str(auth_path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-from-env")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://env.example/v1")

    from dongxuan_agent.web.config import load_settings

    settings = load_settings()

    assert settings.openai_api_key == "sk-test-from-env"
    assert settings.openai_base_url == "https://env.example/v1"


def test_default_auth_path_is_project_local(monkeypatch):
    monkeypatch.delenv("DONGXUAN_CODEX_AUTH_PATH", raising=False)

    from dongxuan_agent.web.config import _candidate_auth_paths

    paths = _candidate_auth_paths()

    assert len(paths) == 1
    assert paths[0].name == "auth.json"
    assert paths[0].parent.name == ".dongxuan"
    assert ".codex" not in str(paths[0])


def test_settings_can_read_model_provider_config_toml(tmp_path, monkeypatch):
    auth_path = tmp_path / "auth.json"
    config_path = tmp_path / "config.toml"
    auth_path.write_text('{"OPENAI_API_KEY": "sk-test-from-file"}', encoding="utf-8")
    config_path.write_text(
        '\n'.join(
            [
                'model_provider = "ai"',
                'model = "gpt-5.5"',
                '',
                '[model_providers.ai]',
                'base_url = "https://aivalux.com"',
                'wire_api = "responses"',
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_WIRE_API", raising=False)
    monkeypatch.setenv("DONGXUAN_CODEX_AUTH_PATH", str(auth_path))
    monkeypatch.setenv("DONGXUAN_CODEX_CONFIG_PATH", str(config_path))

    from dongxuan_agent.web.config import load_settings

    settings = load_settings()

    assert settings.openai_api_key == "sk-test-from-file"
    assert settings.openai_base_url == "https://aivalux.com"
    assert settings.openai_model == "gpt-5.5"
    assert settings.openai_wire_api == "responses"


def test_default_model_timeout_is_long_enough_for_analysis(monkeypatch):
    monkeypatch.delenv("DONGXUAN_REQUEST_TIMEOUT_SECONDS", raising=False)

    from dongxuan_agent.web.config import load_settings

    settings = load_settings()

    assert settings.request_timeout_seconds >= 180


def test_llm_message_requires_numbered_public_analysis_steps():
    from dongxuan_agent.web.llm import _compose_user_message

    message = _compose_user_message(system="bazi", prompt="原始 prompt", context={"question": "问事"})

    assert "编号化公开分析步骤" in message
    assert "确认前置信息" in message
    assert "分析" in message
    assert "结论" in message
    assert "不要单列“不确定项”模块" in message
    assert "不要输出隐藏思维链" in message
    assert "1." in message
    assert "2." in message


def test_frontend_renders_markdown_in_three_stacked_cards():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    for text in ["result-stack", "确认前置信息", "分析", "结论", "renderMarkdown", "splitAnalysisSections"]:
        assert text in html
    assert '<details class="result-card card-context">' in html
    assert '<details class="result-card card-analysis">' in html
    assert '<details class="result-card card-conclusion" open>' in html
    assert "linear-gradient" in html


def _json_roundtrip(value):
    return json.loads(json.dumps(value, ensure_ascii=False))
