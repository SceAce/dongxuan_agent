from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints
from dongxuan_agent.bazi_climate import analyze_climate
from dongxuan_agent.bazi_integration import build_integrated_analysis
from dongxuan_agent.bazi_strength import analyze_strength


def _integration(target_year: int = 2025) -> dict:
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    strength = analyze_strength(chart)
    climate = analyze_climate(chart, strength)
    hints = build_year_analysis_hints(chart, target_year)
    return build_integrated_analysis(chart, strength, climate, hints)


def test_integrated_analysis_exposes_three_layer_structure():
    result = _integration()

    assert set(result) >= {
        "natal_structure",
        "luck_influence",
        "year_influence",
        "integrated_analysis",
        "uncertainty",
    }
    assert result["natal_structure"]["day_master_level"] == "中和"
    assert result["natal_structure"]["climate_need"] == ["火", "燥土"]
    assert "金" in result["natal_structure"]["dominant_forces"]
    assert "木" in result["natal_structure"]["weak_forces"]


def test_luck_and_year_influence_describe_ten_god_climate_and_relations():
    result = _integration()

    luck = result["luck_influence"]
    year = result["year_influence"]

    assert luck["ganzhi"] == "壬寅"
    assert "伤官" in luck["ten_god_theme"]
    assert "正财" in luck["ten_god_theme"]
    assert luck["climate_effect"] == "加重寒湿"
    assert year["ganzhi"] == "乙巳"
    assert year["visible_ten_god"] == "偏财"
    assert "正官" in year["hidden_ten_gods"]
    assert any(item["type"] == "并临" and item["palace"] == "日支" for item in year["triggered_relations"])


def test_integrated_analysis_converges_to_one_main_axis_with_reasoning_chain():
    result = _integration()
    integrated = result["integrated_analysis"]

    assert "财" in integrated["main_axis"]
    assert "日支" in integrated["main_axis"]
    assert len(integrated["reasoning_chain"]) >= 4
    assert any("原局" in item for item in integrated["reasoning_chain"])
    assert any("大运" in item for item in integrated["reasoning_chain"])
    assert any("流年" in item for item in integrated["reasoning_chain"])
    assert len(integrated["event_shape"]) > 0
    assert any("不等于" in item for item in integrated["avoid_overread"])
