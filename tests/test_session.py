import json

from daliuren_session import main


def _extract_json_block(output: str) -> dict:
    start = output.index("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_session_outputs_context_json(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--mode",
        "number",
        "--number",
        "20",
        "--gender",
        "男",
        "--question",
        "测试",
        "--birth-year",
        "1970",
    ]) == 0

    output = capsys.readouterr().out
    payload = _extract_json_block(output)

    assert "## 大六壬工具上下文" in output
    assert payload["divination"]["source_hour_branch"] == "未"
    assert payload["querent"]["life_branch"] == "戌"
    assert payload["calendar"]["hour_branch"] == "未"
    assert "rule_cards" in payload
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
