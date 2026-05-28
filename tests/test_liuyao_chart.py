import pytest

from dongxuan_agent.liuyao import build_liuyao_chart
from dongxuan_agent.liuyao.context import build_liuyao_context


def test_manual_chart_outputs_required_json_without_bazi_or_daliuren_fields():
    chart = build_liuyao_chart(
        lines="少阳 老阴 少阴 少阳 老阳 少阴",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["schema"] == "liuyao_chart_v9"
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
    assert len(chart["derived_lines"]) == 6
    assert chart["useful_god_analysis"]["candidates"]
    assert chart["relations"]["month_day"]["by_line"]
    assert chart["judgment_frame"]["mode"] == "minimal_loop"
    assert "derived_lines" in chart["prompt_contract"]["must_use_fields"]
    assert "useful_god_selection" in chart["prompt_contract"]["must_use_fields"]
    assert "question_template" in chart["prompt_contract"]["must_use_fields"]
    assert "six_spirits" in chart["prompt_contract"]["must_use_fields"]
    assert "spirit_role_analysis" in chart["prompt_contract"]["must_use_fields"]
    assert "twelve_stage_analysis" in chart["prompt_contract"]["must_use_fields"]
    assert "combination_analysis" in chart["prompt_contract"]["must_use_fields"]
    assert "flying_hidden_analysis" in chart["prompt_contract"]["must_use_fields"]
    assert "advance_retreat_analysis" in chart["prompt_contract"]["must_use_fields"]
    assert "completion_chain" in chart["prompt_contract"]["must_use_fields"]
    assert "advanced_layers" in chart["prompt_contract"]["must_use_fields"]
    assert "imagery_context" in chart
    assert "useful_god_selection" in chart
    assert "spirit_role_analysis" in chart
    assert "twelve_stage_analysis" in chart
    assert "combination_analysis" in chart
    assert "flying_hidden_analysis" in chart
    assert "advance_retreat_analysis" in chart
    assert "completion_chain" in chart
    assert chart["advanced_layers"]["enabled"] == ["spirit_roles", "twelve_stages", "three_combination", "flying_hidden", "advance_retreat"]
    assert chart["twelve_stage_analysis"]["enabled"] is True
    assert chart["combination_analysis"]["enabled"] is True
    assert chart["flying_hidden_analysis"]["enabled"] is True
    assert chart["advance_retreat_analysis"]["enabled"] is True
    assert "flying_hidden" not in chart["advanced_layers"]["reserved"]
    assert "advance_retreat" not in chart["advanced_layers"]["reserved"]
    assert "timing" in chart["advanced_layers"]["reserved"]
    assert chart["question_template"]["template_id"] == "career_work"
    assert chart["six_spirits"]["scope"] == "辅助取象，不作主裁决"
    assert chart["auxiliary_marks"]["enabled"] == []
    assert all("six_spirit" in line for line in chart["derived_lines"])
    assert all("spirit_role" in line and "spirit_role_reason" in line for line in chart["derived_lines"])
    assert all("twelve_stage" in line for line in chart["derived_lines"])

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

    assert payload["schema"] == "liuyao_chart_v9"
    assert payload["analysis_hints"]["must_check"]
    assert payload["derived_lines"]


def test_chart_requires_exactly_one_input_mode():
    with pytest.raises(ValueError, match="必须且只能提供一种起卦方式"):
        build_liuyao_chart(
            lines="少阳 老阴 少阴 少阳 老阳 少阴",
            hexagram="离之大有",
            value="2026-05-28 09:30:00",
        )
