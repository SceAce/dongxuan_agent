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


def test_bazi_chart_can_apply_true_solar_time_by_longitude():
    chart = build_bazi_chart(
        "2026-05-26 10:14:15",
        timezone="Asia/Shanghai",
        gender="男",
        longitude=90.0,
    )
    payload = chart.to_dict()

    assert payload["time_adjustment"]["mode"] == "true_solar"
    assert payload["time_adjustment"]["longitude"] == 90.0
    assert payload["calendar"]["hour_gz"] == "庚辰"


def test_bazi_chart_late_zi_hour_changes_day_when_enabled():
    normal = build_bazi_chart("2026-05-25 23:30:00", timezone="Asia/Shanghai", zi_hour_rule="whole")
    split = build_bazi_chart("2026-05-25 23:30:00", timezone="Asia/Shanghai", zi_hour_rule="split")

    assert normal.to_dict()["calendar"]["day_gz"] == "己亥"
    assert normal.to_dict()["calendar"]["hour_gz"] == "甲子"
    assert split.to_dict()["calendar"]["day_gz"] == "庚子"
    assert split.to_dict()["calendar"]["hour_gz"] == "丙子"
    assert split.to_dict()["time_rules"]["zi_hour_rule"] == "split"


def test_bazi_chart_early_zi_hour_keeps_day_when_split_enabled():
    split = build_bazi_chart("2026-05-26 00:30:00", timezone="Asia/Shanghai", zi_hour_rule="split")

    assert split.to_dict()["calendar"]["day_gz"] == "庚子"
    assert split.to_dict()["calendar"]["hour_gz"] == "丙子"


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
