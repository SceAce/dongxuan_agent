import json


def test_case_visibility_is_scoped_by_password_fingerprint(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    monkeypatch.setenv("DONGXUAN_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    a_case = client.post("/api/cases", json={"password": "alice", "title": "Alice 案例", "system": "bazi"}).json()
    b_case = client.post("/api/cases", json={"password": "bob", "title": "Bob 案例", "system": "bazi"}).json()

    assert [item["id"] for item in client.post("/api/cases/list", json={"password": "alice"}).json()] == [a_case["id"]]
    assert [item["id"] for item in client.post("/api/cases/list", json={"password": "bob"}).json()] == [b_case["id"]]
    assert {item["id"] for item in client.post("/api/cases/list", json={"password": "sudo"}).json()} == {a_case["id"], b_case["id"]}

    assert client.post(f"/api/cases/{b_case['id']}/get", json={"password": "alice"}).status_code == 404
    assert client.post(f"/api/cases/{b_case['id']}/get", json={"password": "sudo"}).status_code == 200


def test_password_is_required_for_cases_and_analysis(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())

    assert client.get("/api/cases").status_code == 401
    assert client.post("/api/cases", json={"title": "无密码"}).status_code == 401
    assert client.post("/api/bazi/analyze", json={"datetime": "2006-12-18 12:30:00"}).status_code == 401
    assert client.post("/api/bazi/analyze", json={"password": "alice", "datetime": "2006-12-18 12:30:00"}).status_code == 200


def test_audit_log_records_actions_without_plain_password(tmp_path, monkeypatch):
    monkeypatch.setenv("DONGXUAN_LLM_PROVIDER", "echo")
    monkeypatch.setenv("DONGXUAN_MEMORY_PATH", str(tmp_path / "memory.json"))
    monkeypatch.setenv("DONGXUAN_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    from dongxuan_agent.web.app import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.post("/api/cases", json={"password": "alice-secret", "title": "Alice 案例", "system": "bazi"})

    assert response.status_code == 200
    lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]
    assert payloads[-1]["action"] == "case.create"
    assert payloads[-1]["actor_hash"]
    assert payloads[-1]["case_id"] == response.json()["id"]
    assert "alice-secret" not in "\n".join(lines)
