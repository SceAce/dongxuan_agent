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
    request["password"] = "alice"
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
    request["password"] = "alice"
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

    request = {"password": "alice", "datetime": "2026-05-28 20:00:00", "timezone": "Asia/Shanghai", "mode": "time"}
    expected_context = chart_to_json(build_chart(request["datetime"], timezone=request["timezone"]))
    expected_context["rule_cards"] = build_rule_context(None)

    client = TestClient(create_app())
    request["password"] = "alice"
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


def test_case_api_persists_case_memory(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    created = client.post(
        "/api/cases",
        json={
            "password": "alice",
            "title": "财运案例",
            "system": "bazi",
            "birth": {"datetime": "2006-12-18 12:30:00", "timezone": "Asia/Shanghai", "region": ""},
            "background": "目前关注财运",
            "facts": [{"text": "五月先赚后回撤"}],
            "intents": [{"text": "验证六月走势"}],
        },
    )

    assert created.status_code == 200
    case = created.json()
    assert case["title"] == "财运案例"
    assert case["facts"][0]["confidence"] == "verified"

    listed = client.post("/api/cases/list", json={"password": "alice"})
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == case["id"]

    updated = client.patch(
        f"/api/cases/{case['id']}",
        json={"password": "alice", "background": "金融短线", "notes": {"summary": "围绕财务波动追问。"}},
    )
    assert updated.status_code == 200
    assert updated.json()["background"] == "金融短线"
    assert updated.json()["notes"]["summary"] == "围绕财务波动追问。"


def test_case_bazi_analysis_injects_memory_and_appends_record(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    case = client.post(
        "/api/cases",
        json={
            "password": "alice",
            "title": "财运案例",
            "system": "bazi",
            "background": "金融短线",
            "facts": [{"text": "五月先赚后回撤"}],
            "intents": [{"text": "验证六月走势"}],
        },
    ).json()

    response = client.post(
        f"/api/cases/{case['id']}/bazi/analyze",
        json={
            "password": "alice",
            "datetime": "2006-12-18 12:30:00",
            "timezone": "Asia/Shanghai",
            "question": "继续看六月财运",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["case_memory"]["background"] == "金融短线"
    assert payload["context"]["case_memory"]["facts"][0]["text"] == "五月先赚后回撤"
    assert "echo provider" in payload["analysis"]

    stored = client.post(f"/api/cases/{case['id']}/get", json={"password": "alice"}).json()
    assert stored["records"][-1]["question"] == "继续看六月财运"
    assert stored["records"][-1]["context"]["case_memory"]["intents"][0]["text"] == "验证六月走势"


def test_case_bazi_analysis_extracts_target_year_from_question_and_persists_chart(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    case = client.post("/api/cases", json={"password": "alice", "title": "学业案例", "system": "bazi"}).json()

    response = client.post(
        f"/api/cases/{case['id']}/bazi/analyze",
        json={
            "password": "alice",
            "datetime": "2006-11-05 06:00:00",
            "timezone": "Asia/Shanghai",
            "gender": "男",
            "question": "看看桃花运如何？什么时候能脱单，结合2026年分析",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["analysis_hints"]["target_year"] == 2026
    assert "luck_year_remedy" in payload["context"]

    stored = client.post(f"/api/cases/{case['id']}/get", json={"password": "alice"}).json()
    assert stored["bazi"]["pillars"]
    assert stored["luck"]["cycles"]
    assert stored["notes"]["year_hints"]["2026"]["target_year"] == 2026


def test_model_errors_are_returned_as_json(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    import dongxuan_agent.web.app as web_app
    from fastapi.testclient import TestClient

    def broken_analyze_bazi(request, adapter):
        raise RuntimeError("模型接口返回 401，请检查 OPENAI_API_KEY")

    monkeypatch.setattr(web_app, "analyze_bazi", broken_analyze_bazi)

    client = TestClient(web_app.create_app())
    response = client.post("/api/bazi/analyze", json={"password": "alice", "datetime": "2006-12-18 12:30:00"})

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


def test_default_model_output_budget_is_large_enough(monkeypatch):
    monkeypatch.delenv("DONGXUAN_MAX_OUTPUT_TOKENS", raising=False)

    from dongxuan_agent.web.config import load_settings

    settings = load_settings()

    assert settings.max_output_tokens >= 4096


def test_llm_message_requires_numbered_public_analysis_steps():
    from dongxuan_agent.web.llm import _compose_user_message

    message = _compose_user_message(system="bazi", prompt="原始 prompt", context={"question": "问事"})

    assert "编号化公开分析步骤" in message
    assert "确认前置信息" in message
    assert "分析" in message
    assert "结论" in message
    assert "结论必须通俗易懂" in message
    assert "不要堆字段名" in message
    assert "优先保证结论完整" in message
    assert "已验证事实 Fact 优先级高于旧判断" in message
    assert "待验证事实 Intent 不能当成已经发生" in message
    assert "不要单列“不确定项”模块" in message
    assert "不要输出隐藏思维链" in message
    assert "1." in message
    assert "2." in message


def test_responses_request_sets_large_output_budget(monkeypatch):
    from dongxuan_agent.web.config import WebSettings
    from dongxuan_agent.web.llm import OpenAILLMAdapter

    captured = {}

    class FakeResponse:
        pass

    def fake_post(url, *, headers, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("dongxuan_agent.web.llm.httpx.post", fake_post)
    settings = WebSettings(
        access_password=None,
        llm_provider="openai",
        openai_api_key="sk-test",
        openai_base_url="https://aivalux.com",
        openai_model="gpt-5.5",
        openai_wire_api="responses",
        request_timeout_seconds=240,
        max_question_length=2000,
        max_output_tokens=8192,
    )

    adapter = OpenAILLMAdapter(settings)
    adapter._post_responses(system="bazi", prompt="prompt", context={"question": "问事"})

    assert captured["url"] == "https://aivalux.com/responses"
    assert captured["json"]["max_output_tokens"] == 8192
    assert captured["timeout"] == 240


def test_frontend_renders_markdown_in_three_stacked_cards():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    for text in ["result-stack", "确认前置信息", "分析", "结论", "renderMarkdown", "splitAnalysisSections"]:
        assert text in html
    assert '<details class="result-card card-context">' in html
    assert '<details class="result-card card-analysis">' in html
    assert '<details class="result-card card-conclusion" open>' in html
    assert "linear-gradient" in html


def test_frontend_supports_local_conversation_switching_without_backend_writes():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    for text in [
        "conversation-list",
        "新建对话",
        "确认密码",
        "passwordConfirmed",
        "confirm-password",
        "loadConversations",
        "saveActiveConversation",
        "switchConversation",
        "deleteConversation",
        "/api/cases",
        "/api/cases/list",
        "datetime_parts",
        "composeDatetime",
        "writeDatetimeParts",
        "normalizeMemoryLines",
        "如果第一次使用",
        "已验证事实",
        "待验证事实",
        "背景",
    ]:
        assert text in html
    assert "管理员可输入 sudo 查看全部" not in html
    assert "/api/session" not in html


def test_frontend_can_switch_between_question_nodes():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    for text in [
        "node-list",
        "问题节点",
        "renderNodeList",
        "showRecordNode",
        "activeRecordId",
        "当前节点",
        "refreshActiveConversation",
        "data-record-id",
    ]:
        assert text in html
    assert "records[records.length - 1]" in html


def test_frontend_saves_plain_error_text_not_error_html():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    assert "const errorAnalysis = `## 结论\\n${error.message}`" in html
    assert "saveActiveConversation({ analysis: errorAnalysis" in html


def test_frontend_avoids_redundant_case_save_after_successful_analysis():
    from pathlib import Path

    html = Path("dongxuan_agent/web/static/index.html").read_text(encoding="utf-8")

    assert "await refreshActiveConversation();" in html
    assert "const usesCaseEndpoint" in html
    assert "if (usesCaseEndpoint)" in html
    assert "await saveActiveConversation({ analysis: data.analysis, contextText: context.textContent });\n          await refreshActiveConversation();" not in html
    assert "state.saveInFlight" in html
    assert "state.saveQueued" in html
    assert "if (state.saveInFlight)" in html


def test_index_page_is_not_cached_so_frontend_updates_are_visible(monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "conversation-list" in response.text


def _json_roundtrip(value):
    return json.loads(json.dumps(value, ensure_ascii=False))
