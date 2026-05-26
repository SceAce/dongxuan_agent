from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints


def test_year_analysis_hints_for_2006_birth_target_2025():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    hints = build_year_analysis_hints(chart, target_year=2025)

    assert hints["target_year"] == 2025
    assert hints["year_ganzhi"] == "乙巳"
    assert hints["current_luck"]["ganzhi"] == "壬寅"
    assert hints["flow_year"]["ganzhi"] == "乙巳"
    assert hints["flow_year"]["stem_ten_god"] == "偏财"
    assert {"stem": "丙", "ten_god": "正官"} in hints["flow_year"]["hidden_stems"]
    assert any(
        item["field"] == "流年支与日支" and item["type"] == "并临"
        for item in hints["activated_relations"]
    )
    assert any(item["palace"] == "日支" for item in hints["activated_palaces"])
    assert any(item["domain"] == "学业/考试/规则压力" for item in hints["event_candidates"])
    assert any(item["domain"] == "财务/资源/男命关系议题" for item in hints["event_candidates"])
    assert any(item["domain"] == "状态变化/环境触发" for item in hints["event_candidates"])


def test_year_analysis_hints_marks_conflicts_and_evidence():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    hints = build_year_analysis_hints(chart, target_year=2025)

    assert hints["conflicts"]
    assert any("刑动不可单独定凶" in item for item in hints["conflicts"])
    assert all(item["strength"] > 0 for item in hints["event_candidates"])
    assert all(item["evidence"] for item in hints["event_candidates"])
