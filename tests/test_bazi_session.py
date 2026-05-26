import json

from bazi_session import main


def _extract_json(output: str) -> dict:
    start = output.index("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_bazi_session_outputs_chart_hints_and_rule_cards(capsys):
    assert main([
        "2006-12-18 12:30:00",
        "--gender",
        "男",
        "--target-year",
        "2025",
        "--question",
        "推断2025年发生了什么",
    ]) == 0
    payload = _extract_json(capsys.readouterr().out)

    assert payload["calendar"]["year_gz"] == "丙戌"
    assert payload["strength_analysis"]["day_master_strength"]["day_master"] == "辛"
    assert payload["climate_analysis"]["season_profile"] == "子月寒水当令"
    assert payload["pattern_analysis"]["primary_pattern"]["name"] == "食神格"
    assert payload["analysis_hints"]["target_year"] == 2025
    assert payload["analysis_hints"]["year_ganzhi"] == "乙巳"
    assert payload["integrated_analysis"]["luck_influence"]["ganzhi"] == "壬寅"
    assert "财" in payload["integrated_analysis"]["integrated_analysis"]["main_axis"]
    assert payload["rule_cards"]["mode"] == "year_event"


def test_bazi_session_can_include_prompt(capsys):
    assert main([
        "2006-12-18 12:30:00",
        "--gender",
        "男",
        "--target-year",
        "2025",
        "--include-prompt",
    ]) == 0
    output = capsys.readouterr().out

    assert "# 八字年份事件分析 Prompt" in output
    assert "## 八字工具上下文" in output
