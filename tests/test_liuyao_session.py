import json

from liuyao_session import main as session_main


def _extract_json(output: str) -> dict:
    if "```json" not in output:
        return json.loads(output)
    start = output.index("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_liuyao_session_outputs_prompt_and_json(capsys):
    assert session_main([
        "--hexagram",
        "离之大有",
        "--question",
        "问合同",
        "--datetime",
        "2026-05-28 09:30:00",
        "--include-prompt",
    ]) == 0

    output = capsys.readouterr().out
    payload = _extract_json(output)

    assert "# 六爻分析 Prompt" in output
    assert "## 六爻工具上下文" in output
    assert "不得使用八字旺衰" in output
    assert "不得使用大六壬四课" in output
    assert payload["schema"] == "liuyao_chart_v9"
    assert payload["derived_lines"]
    assert payload["useful_god_analysis"]["candidates"]
    assert payload["useful_god_selection"]
    assert payload["question_template"]
    assert payload["six_spirits"]
    assert payload["spirit_role_analysis"]
    assert payload["twelve_stage_analysis"]
    assert payload["combination_analysis"]
    assert payload["flying_hidden_analysis"]
    assert payload["advance_retreat_analysis"]
    assert payload["completion_chain"]
