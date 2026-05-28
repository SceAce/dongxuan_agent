import pytest

from dongxuan_agent.liuyao import build_liuyao_chart
from dongxuan_agent.liuyao.context import build_liuyao_context


def test_manual_chart_outputs_required_json_without_bazi_or_daliuren_fields():
    chart = build_liuyao_chart(
        lines="少阳 老阴 少阴 少阳 老阳 少阴",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["schema"] == "liuyao_chart_v1"
    assert chart["input"]["method"] == "manual_lines"
    assert chart["input"]["line_order"] == "bottom_to_top"
    assert chart["calendar"]["year_gz"]
    assert chart["calendar"]["month_branch"] == chart["calendar"]["month_gz"][1]
    assert chart["calendar"]["day_branch"] == chart["calendar"]["day_gz"][1]
    assert chart["hexagram"]["moving_lines"] == [2, 5]
    assert chart["lines"][1]["input_state"] == "老阴"
    assert chart["lines"][1]["moving"] is True
    assert chart["question_context"]["domain"] == "事业/工作"
    assert "官鬼" in [item["six_relative"] for item in chart["question_context"]["candidate_useful_gods"]]

    forbidden = {
        "strength_analysis",
        "climate_analysis",
        "pattern_analysis",
        "remedy_analysis",
        "god_candidates",
        "luck_year_remedy",
        "discipline_profile",
        "four_lessons",
        "transmissions",
        "heavenly_officers",
    }
    assert forbidden.isdisjoint(chart)


def test_named_hexagram_chart_preserves_original_changed_and_moving_lines():
    chart = build_liuyao_chart(
        hexagram="离之大有",
        question="问合同",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["input"]["method"] == "named_hexagram"
    assert chart["hexagram"]["original"]["name"] == "离为火"
    assert chart["hexagram"]["changed"]["name"] == "火天大有"
    assert chart["hexagram"]["moving_lines"] == [2]
    assert chart["lines"][1]["moving"] is True


def test_random_chart_accepts_seed_for_repeatable_tests():
    chart = build_liuyao_chart(
        random_lines=True,
        seed=7,
        question="问财运",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["input"]["method"] == "random_lines"
    assert len(chart["lines"]) == 6
    assert {line["input_state"] for line in chart["lines"]} <= {"老阴", "少阳", "少阴", "老阳"}


def test_context_wraps_chart_and_hints():
    payload = build_liuyao_context(
        lines="少阳 老阴 少阴 少阳 老阳 少阴",
        question="问工作",
        value="2026-05-28 09:30:00",
    )

    assert payload["schema"] == "liuyao_chart_v1"
    assert payload["analysis_hints"]["must_check"]


def test_chart_requires_exactly_one_input_mode():
    with pytest.raises(ValueError, match="必须且只能提供一种起卦方式"):
        build_liuyao_chart(
            lines="少阳 老阴 少阴 少阳 老阳 少阴",
            hexagram="离之大有",
            value="2026-05-28 09:30:00",
        )
