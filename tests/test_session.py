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


def test_session_can_include_prompt(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--include-prompt",
    ]) == 0

    output = capsys.readouterr().out

    assert "# 大六壬测算 Prompt" in output
    assert "没有课盘，不做断语" in output
    assert "## 大六壬工具上下文" in output
