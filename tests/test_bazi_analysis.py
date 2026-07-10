import subprocess
import sys

import pytest

from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi.year import build_year_analysis_hints


def test_bazi_year_does_not_import_daliuren_domain():
    script = (
        "import sys; "
        "import dongxuan_agent.bazi.year; "
        "print('dongxuan_agent.daliuren.divination' in sys.modules)"
    )

    result = subprocess.run([sys.executable, "-c", script], check=True, capture_output=True, text=True)

    assert result.stdout.strip() == "False"


def test_year_analysis_hints_for_2006_birth_target_2025():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    hints = build_year_analysis_hints(chart, target_year=2025)

    assert hints["target_year"] == 2025
    assert hints["year_ganzhi"] == "乙巳"
    assert hints["current_luck"]["ganzhi"] == "壬寅"
    assert hints["luck_status"]["status"] == "matched"
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


def test_year_before_birth_is_rejected():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")

    with pytest.raises(ValueError, match="目标年份不能早于出生年份"):
        build_year_analysis_hints(chart, 2005)


def test_year_before_luck_start_has_no_current_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")

    hints = build_year_analysis_hints(chart, 2006)

    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "not_started"
    assert hints["luck_status"]["virtual_age"] == 1


def test_year_beyond_generated_cycles_has_no_fallback_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")

    hints = build_year_analysis_hints(chart, 2200)

    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "out_of_range"


def test_year_without_gender_reports_unavailable_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00")

    hints = build_year_analysis_hints(chart, 2025)

    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "unavailable"
