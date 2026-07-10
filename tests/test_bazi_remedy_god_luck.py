from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi.climate import analyze_climate
from dongxuan_agent.bazi.gods import build_god_candidates
from dongxuan_agent.bazi.luck_remedy import analyze_luck_year_remedy
from dongxuan_agent.bazi.pattern import analyze_pattern
from dongxuan_agent.bazi.remedy import analyze_remedy
from dongxuan_agent.bazi.strength import analyze_strength
from dongxuan_agent.bazi.year import build_year_analysis_hints


def _fixture(target_year: int = 2025):
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    strength = analyze_strength(chart)
    climate = analyze_climate(chart, strength)
    pattern = analyze_pattern(chart)
    remedy = analyze_remedy(strength, climate, pattern)
    gods = build_god_candidates(remedy, strength, climate, pattern)
    hints = build_year_analysis_hints(chart, target_year)
    luck_year = analyze_luck_year_remedy(chart, remedy, gods, hints)
    return remedy, gods, luck_year


def test_remedy_analysis_identifies_climate_strength_and_pattern_problems():
    remedy, _, _ = _fixture()

    assert any(problem["type"] == "调候病" and "寒湿" in problem["description"] for problem in remedy["problems"])
    assert any(candidate["element"] == "火" and candidate["role"] == "调候药" for candidate in remedy["remedy_candidates"])
    assert any(candidate["element"] == "燥土" for candidate in remedy["remedy_candidates"])
    assert any("午火" in item for item in remedy["conflicts"])
    assert remedy["priority"] == "调候优先"
    assert remedy["status"] == "候选病药，不作最终用神定论"


def test_god_candidates_score_and_mark_candidate_status():
    _, gods, _ = _fixture()

    elements = [item["element"] for item in gods["candidate_gods"]]

    assert elements[0] == "火"
    assert "燥土" in elements
    assert "水" in gods["avoid_gods"]
    assert gods["priority"] == "调候优先"
    assert gods["status"] == "候选用神，不作最终定论"
    assert any("调候" in item for item in gods["supporting_evidence"])


def test_luck_year_remedy_marks_luck_as_adding_problem_and_year_as_mixed():
    _, _, luck_year = _fixture()

    assert luck_year["luck_effect_on_remedy"]["ganzhi"] == "壬寅"
    assert luck_year["luck_effect_on_remedy"]["effect"] == "加病"
    assert luck_year["year_effect_on_remedy"]["ganzhi"] == "乙巳"
    assert luck_year["year_effect_on_remedy"]["effect"] in {"来药", "药病并见"}
    assert luck_year["combined_effect"] == "药病并见"
    assert any("大运" in item for item in luck_year["reasoning_chain"])
    assert any("流年" in item for item in luck_year["reasoning_chain"])


def test_luck_year_remedy_uses_luck_status_when_luck_has_not_started():
    _, _, luck_year = _fixture(target_year=2006)

    luck_effect = luck_year["luck_effect_on_remedy"]
    assert luck_effect["ganzhi"] is None
    assert luck_effect["effect"] == "未知"
    assert any("目标年份尚未起运" in item for item in luck_effect["evidence"])
    assert luck_year["year_effect_on_remedy"]["ganzhi"] == "丙戌"
