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


def _json_roundtrip(value):
    return json.loads(json.dumps(value, ensure_ascii=False))
