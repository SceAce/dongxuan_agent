import pytest

from dongxuan_agent.bazi import build_bazi_chart


def test_bazi_chart_exposes_four_pillars_day_master_and_xunkong():
    chart = build_bazi_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()

    assert payload["calendar"]["year_gz"] == "丙午"
    assert payload["calendar"]["month_gz"] == "癸巳"
    assert payload["calendar"]["day_gz"] == "庚子"
    assert payload["calendar"]["hour_gz"] == "辛巳"
    assert payload["day_master"] == "庚"
    assert payload["xunkong"] == ["辰", "巳"]
    assert [pillar["name"] for pillar in payload["pillars"]] == ["年柱", "月柱", "日柱", "时柱"]


def test_bazi_chart_exposes_ten_gods_for_stems_and_hidden_stems():
    chart = build_bazi_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()

    by_name = {pillar["name"]: pillar for pillar in payload["pillars"]}

    assert by_name["年柱"]["stem"] == "丙"
    assert by_name["年柱"]["stem_ten_god"] == "七杀"
    assert by_name["月柱"]["stem"] == "癸"
    assert by_name["月柱"]["stem_ten_god"] == "伤官"
    assert by_name["日柱"]["stem_ten_god"] == "日主"
    assert by_name["时柱"]["stem"] == "辛"
    assert by_name["时柱"]["stem_ten_god"] == "劫财"
    assert by_name["日柱"]["hidden_stems"] == [{"stem": "癸", "ten_god": "伤官"}]
    assert {"stem": "丙", "ten_god": "七杀"} in by_name["月柱"]["hidden_stems"]


def test_bazi_chart_exposes_branch_relationships():
    chart = build_bazi_chart("2026-05-26 11:14:15", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()
    relationships = {
        (item["type"], item["branches"])
        for item in payload["branch_relationships"]
    }

    assert ("冲", "子午") in relationships
    assert ("自刑", "午午") in relationships


def test_bazi_chart_exposes_branch_combine():
    chart = build_bazi_chart("2026-05-26 15:14:15", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()
    relationships = {
        (item["type"], item["branches"])
        for item in payload["branch_relationships"]
    }

    assert ("合", "巳申") in relationships


def test_bazi_chart_can_apply_longitude_approximation():
    chart = build_bazi_chart(
        "2026-05-26 10:14:15",
        timezone="Asia/Shanghai",
        gender="男",
        longitude=90.0,
    )
    payload = chart.to_dict()

    assert payload["time_adjustment"]["mode"] == "longitude_approximation"
    assert payload["time_adjustment"]["longitude"] == 90.0
    assert payload["calendar"]["hour_gz"] == "庚辰"


def test_bazi_chart_uses_midnight_as_day_boundary_for_zi_hour():
    late = build_bazi_chart("2026-05-25 23:30:00", timezone="Asia/Shanghai")
    early = build_bazi_chart("2026-05-26 00:30:00", timezone="Asia/Shanghai")

    assert late.calendar.day_gz == "己亥"
    assert late.calendar.hour_gz == "甲子"
    assert early.calendar.day_gz == "庚子"
    assert early.calendar.hour_gz == "丙子"
    assert late.time_rules == {
        "day_boundary": "24:00",
        "zi_hour_rule": "early_late_split",
        "note": "早晚子时，以 24:00 为日界；23:00-23:59 属当天晚子时，00:00-00:59 属当日早子时。",
    }


@pytest.mark.parametrize("longitude", [-180.0, 180.0])
def test_bazi_chart_accepts_longitude_boundaries(longitude):
    assert build_bazi_chart("2026-05-26 10:14:15", longitude=longitude)


@pytest.mark.parametrize("longitude", [-180.01, 180.01, float("nan"), float("inf"), float("-inf")])
def test_bazi_chart_rejects_invalid_longitude(longitude):
    with pytest.raises(ValueError, match="经度必须是 -180 到 180 之间的有限数"):
        build_bazi_chart("2026-05-26 10:14:15", longitude=longitude)


def test_bazi_chart_exposes_dayun_direction_and_start():
    male = build_bazi_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai", gender="男")
    female = build_bazi_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai", gender="女")
    male_payload = male.to_dict()
    female_payload = female.to_dict()

    assert male_payload["luck"]["direction"] == "顺"
    assert female_payload["luck"]["direction"] == "逆"
    assert male_payload["luck"]["start"]["days_to_boundary"] > 0
    assert male_payload["luck"]["start"]["start_age_years"] > 0
    assert [item["ganzhi"] for item in male_payload["luck"]["cycles"][:3]] == ["甲午", "乙未", "丙申"]
    assert [item["ganzhi"] for item in female_payload["luck"]["cycles"][:3]] == ["壬辰", "辛卯", "庚寅"]
