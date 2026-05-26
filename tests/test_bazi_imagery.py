from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints
from dongxuan_agent.bazi_climate import analyze_climate
from dongxuan_agent.bazi_god import build_god_candidates
from dongxuan_agent.bazi_imagery import build_imagery_analysis
from dongxuan_agent.bazi_integration import build_integrated_analysis
from dongxuan_agent.bazi_luck_remedy import analyze_luck_year_remedy
from dongxuan_agent.bazi_pattern import analyze_pattern
from dongxuan_agent.bazi_remedy import analyze_remedy
from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context
from dongxuan_agent.bazi_strength import analyze_strength


def _payload(question="推断2025年发生了什么"):
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    strength = analyze_strength(chart)
    climate = analyze_climate(chart, strength)
    pattern = analyze_pattern(chart)
    remedy = analyze_remedy(strength, climate, pattern)
    gods = build_god_candidates(remedy, strength, climate, pattern)
    hints = build_year_analysis_hints(chart, 2025)
    integration = build_integrated_analysis(chart, strength, climate, hints)
    luck_year = analyze_luck_year_remedy(chart, remedy, gods, hints)
    rule_cards = build_bazi_rule_context(question, 2025)
    return {
        "chart": chart.to_dict(),
        "strength_analysis": strength,
        "climate_analysis": climate,
        "pattern_analysis": pattern,
        "remedy_analysis": remedy,
        "god_candidates": gods,
        "analysis_hints": hints,
        "integrated_analysis": integration,
        "luck_year_remedy": luck_year,
        "rule_cards": rule_cards,
        "question": question,
    }


def test_imagery_converges_to_main_and_secondary_images_with_evidence():
    result = build_imagery_analysis(_payload())

    assert result["question_domain"] in {"year_event", "general_year"}
    assert result["main_image"]["domain"] in {"技术/项目/竞赛", "资源/目标/关系"}
    assert result["main_image"]["evidence"]
    assert result["secondary_image"]["evidence"]
    assert len(result["candidate_images"]) >= 2
    assert all(item["evidence"] for item in result["candidate_images"])


def test_imagery_evidence_is_structured_and_traceable_to_fields():
    result = build_imagery_analysis(_payload())

    for item in [result["main_image"], result["secondary_image"], *result["candidate_images"]]:
        for evidence in item["evidence"]:
            assert set(evidence) >= {"source_field", "source_value", "rule", "text"}
            assert evidence["source_field"]
            assert evidence["text"]


def test_imagery_uses_modern_age_context_without_claiming_unproven_facts():
    result = build_imagery_analysis(_payload())

    assert result["context_frame"]["age_stage"] == "大学/训练期"
    assert "课程" in result["context_frame"]["modern_context"]
    assert "项目" in result["context_frame"]["modern_context"]
    assert any("虚岁 20" in item["text"] for item in result["context_frame"]["evidence"])
    assert any("不能仅凭财星直接断恋爱或得财" in item for item in result["avoid_images"])


def test_imagery_question_domain_can_bias_school_topic():
    result = build_imagery_analysis(_payload("2025年学业和竞赛怎么样"))

    assert result["question_domain"] == "学业/考试/竞赛"
    assert result["main_image"]["domain"] in {"学业/考试/竞赛", "技术/项目/竞赛"}
