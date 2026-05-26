from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_climate import analyze_climate
from dongxuan_agent.bazi_strength import analyze_strength


def test_element_forces_track_real_roots_and_effective_power():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    analysis = analyze_strength(chart)

    metal = analysis["element_forces"]["金"]

    assert metal["count"] >= 3
    assert metal["root_status"] == "有真根"
    assert any(root["branch"] == "戌" and root["quality"] == "真根" for root in metal["roots"])
    assert any(root["branch"] == "巳" and root["quality"] == "余根" for root in metal["roots"])
    assert metal["effective_power"] > analysis["element_forces"]["木"]["effective_power"]


def test_day_master_strength_uses_support_drain_and_root_summary():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    analysis = analyze_strength(chart)
    day_master = analysis["day_master_strength"]

    assert day_master["day_master"] == "辛"
    assert day_master["level"] in {"中和", "中和偏旺", "中和偏弱"}
    assert day_master["support_power"] > 0
    assert day_master["drain_power"] > 0
    assert "戌" in day_master["root_summary"]
    assert "子月不得令" in "；".join(day_master["evidence"])


def test_root_damage_marks_branch_conflict_without_erasing_root():
    chart = build_bazi_chart("2026-05-26 11:14:15", timezone="Asia/Shanghai", gender="男")
    analysis = analyze_strength(chart)

    fire_roots = analysis["element_forces"]["火"]["roots"]

    assert any(root["branch"] == "午" and root["damaged"] for root in fire_roots)
    assert any("午午" in note or "子午" in note for note in analysis["element_forces"]["火"]["damage_notes"])


def test_climate_uses_effective_power_not_only_element_counts():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    strength = analyze_strength(chart)
    climate = analyze_climate(chart, strength)

    assert climate["season_profile"] == "子月寒水当令"
    assert climate["temperature"] == "偏寒"
    assert climate["moisture"] == "偏湿"
    assert "火" in climate["preferred_elements"]
    assert "燥土" in climate["preferred_elements"]
    assert "巳午火" in "；".join(climate["evidence"])
