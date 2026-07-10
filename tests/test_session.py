import json

from daliuren_session import main


def _extract_json_block(output: str) -> dict:
    start = output.rindex("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_session_outputs_context_json(capsys, available_knowledge_root):
    assert main([
        "2026-05-26 10:14:15",
        "--mode",
        "number",
        "--number",
        "9",
        "--question",
        "测试",
        "--birth-year",
        "1970",
    ]) == 0

    output = capsys.readouterr().out
    payload = _extract_json_block(output)

    assert "## 大六壬工具上下文" in output
    assert "## 大六壬测算输入" in output
    assert "### 天地盘" in output
    assert "### 四课" in output
    assert "### 三传" in output
    assert "| 传 | 神 | 遁干 | 旺衰 | 天将 | 天官 | 六亲 |" in output
    assert payload["divination"]["source_hour_branch"] == "巳"
    assert payload["querent"]["life_branch"] == "戌"
    assert payload["calendar"]["hour_branch"] == "巳"
    assert "rule_cards" in payload
    assert "knowledge_layers" in payload
    assert payload["knowledge_layers"]["layer_priority"] == ["理法", "象根", "案例"]
    assert payload["knowledge_layers"]["availability"]["status"] == "available"
    assert all(not page["source"].startswith("/") for page in payload["knowledge_layers"]["topic_pages"])
    assert "/home/source" not in json.dumps(payload["knowledge_layers"], ensure_ascii=False)
    assert payload["rule_cards"]["question_type"] == "通用"
    assert payload["rule_cards"]["cards"]


def test_session_can_include_prompt(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--include-prompt",
    ]) == 0

    output = capsys.readouterr().out

    assert "# 大六壬测算 Prompt" in output
    assert "没有课盘，不做断语" in output
    assert "## 大六壬工具上下文" in output


def test_session_attaches_issue_specific_rule_cards(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--mode",
        "time",
        "--gender",
        "男",
        "--question",
        "最近身体健康怎么样",
        "--birth-year",
        "2005",
    ]) == 0

    output = capsys.readouterr().out
    payload = _extract_json_block(output)
    rule_cards = payload["rule_cards"]
    names = {card["name"] for card in rule_cards["cards"]}
    health_card = next(card for card in rule_cards["cards"] if card["name"] == "病符")

    assert rule_cards["question_type"] == "疾病健康"
    assert "病符" in names
    assert "天医" in names
    assert "白虎" in names
    assert health_card["avoid"]
    assert health_card["sources"]
