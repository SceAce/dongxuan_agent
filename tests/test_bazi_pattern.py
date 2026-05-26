from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_pattern import analyze_pattern


def test_pattern_uses_month_branch_main_qi_as_primary_candidate():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    result = analyze_pattern(chart)

    assert result["month_branch"] == "子"
    assert result["month_main_stem"] == "癸"
    assert result["primary_pattern"]["name"] == "食神格"
    assert result["primary_pattern"]["source"] == "月令本气"
    assert any(item["name"] == "食神格" for item in result["candidate_patterns"])


def test_pattern_records_formation_damage_and_uncertainty():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    result = analyze_pattern(chart)

    assert any("月令子中癸" in item for item in result["formation_evidence"])
    assert any("月干庚为劫财" in item for item in result["damage_evidence"])
    assert result["status"] in {"格局初成", "格局有扰", "格局待定"}
    assert any("V1" in item for item in result["uncertainty"])


def test_pattern_can_identify_jianlu_or_yangren_from_month_branch():
    chart = build_bazi_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai", gender="男")
    result = analyze_pattern(chart)

    assert result["month_branch"] == "巳"
    assert result["primary_pattern"]["name"] in {"七杀格", "偏印格", "比劫格", "建禄格"}
    assert result["primary_pattern"]["confidence"] in {"中", "低"}
    assert result["candidate_patterns"]
