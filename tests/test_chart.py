from dongxuan_agent.chart import build_chart
from dongxuan_agent.divination import (
    build_divination,
    calculate_querent,
    number_to_hour_branch,
)


def test_build_chart_contains_core_sections():
    chart = build_chart("2026-05-25 12:30", timezone="Asia/Shanghai")

    assert chart.calendar.hour_branch == "午"
    assert chart.month_general in "子丑寅卯辰巳午未申酉戌亥"
    assert set(chart.heaven_plate.keys()) == set("子丑寅卯辰巳午未申酉戌亥")
    assert len(chart.four_lessons) == 4
    assert len(chart.heavenly_generals) == 12
    assert chart.xunkong == chart.calendar.xunkong


def test_four_lessons_are_named_and_have_upper_lower():
    chart = build_chart("2026-05-25 12:30", timezone="Asia/Shanghai")

    assert [lesson.name for lesson in chart.four_lessons] == ["一课", "二课", "三课", "四课"]
    assert all(lesson.lower for lesson in chart.four_lessons)
    assert all(lesson.upper in "子丑寅卯辰巳午未申酉戌亥" for lesson in chart.four_lessons)


def test_four_lessons_use_day_stem_lodging_palace():
    chart = build_chart("2026-05-25 23:43:24", timezone="Asia/Shanghai")

    assert chart.calendar.day_gz == "己亥"
    assert chart.calendar.hour_gz == "甲子"
    assert [(lesson.lower, lesson.upper) for lesson in chart.four_lessons] == [
        ("己", "卯"),
        ("卯", "亥"),
        ("亥", "未"),
        ("未", "卯"),
    ]


def test_shehai_selects_deeper_candidate_for_current_chart():
    chart = build_chart("2026-05-25 23:43:24", timezone="Asia/Shanghai")

    assert chart.transmissions.method == "涉害"
    assert chart.transmissions.status == "complete"
    assert chart.transmissions.items == ("未", "卯", "亥")
    assert "涉害" in chart.transmissions.note


def test_chart_exposes_twelve_heavenly_officers():
    chart = build_chart("2026-05-25 23:43:24", timezone="Asia/Shanghai")

    assert len(chart.heavenly_officers) == 12
    assert chart.heavenly_officers["子"]["short"] == "贵"
    assert chart.heavenly_officers["子"]["name"] == "贵人"
    assert chart.heavenly_officers["子"]["heaven"] == "申"


def test_heavenly_officers_are_mounted_on_heaven_plate_branch():
    chart = build_chart("2026-05-26 00:09:14", timezone="Asia/Shanghai")

    assert chart.nobleman["used"] == "未"
    assert chart.heaven_plate["亥"] == "未"
    assert chart.nobleman["direction"] == "顺布"
    assert chart.heavenly_generals["亥"] == "贵"
    assert chart.heavenly_officers["亥"]["name"] == "贵人"


def test_nobleman_reverses_when_mounted_in_si_to_xu():
    chart = build_chart("2026-05-26 09:09:14", timezone="Asia/Shanghai")

    assert chart.nobleman["used"] == "丑"
    assert chart.heaven_plate["戌"] == "丑"
    assert chart.nobleman["direction"] == "逆布"
    assert chart.heavenly_generals["戌"] == "贵"
    assert chart.heavenly_generals["酉"] == "蛇"


def test_day_nobleman_uses_mao_to_shen_hour_branches():
    chart = build_chart("2026-05-26 05:09:14", timezone="Asia/Shanghai")

    assert chart.calendar.hour_branch == "卯"
    assert chart.nobleman["used"] == chart.nobleman["day_noble"]
    assert chart.nobleman["mode"] == "day"


def test_chart_exposes_six_relatives_for_heaven_plate():
    chart = build_chart("2026-05-26 00:09:14", timezone="Asia/Shanghai")

    assert len(chart.six_relatives) == 12
    assert chart.six_relatives["亥"]["heaven"] == "未"
    assert chart.six_relatives["亥"]["relative"] == "父母"
    assert chart.six_relatives["子"]["heaven"] == "申"
    assert chart.six_relatives["子"]["relative"] == "兄弟"


def test_transmissions_include_generals_and_six_relatives():
    chart = build_chart("2026-05-26 00:09:14", timezone="Asia/Shanghai")

    assert [item["branch"] for item in chart.transmission_details] == ["子", "申", "辰"]
    assert chart.transmission_details[0]["general"] == "龙"
    assert chart.transmission_details[0]["officer"] == "青龙"
    assert chart.transmission_details[0]["relative"] == "子孙"


def test_three_transmissions_exposes_status_instead_of_fabricating():
    chart = build_chart("2026-05-25 12:30", timezone="Asia/Shanghai")

    assert chart.transmissions.status in {"complete", "partial", "unsupported"}
    assert len(chart.transmissions.items) == 3
    if chart.transmissions.status != "complete":
        assert chart.transmissions.note


def test_transmission_method_names_are_from_jiuzongmen():
    seen = set()
    for hour in range(0, 24, 2):
        chart = build_chart(f"2026-05-25 {hour:02d}:30", timezone="Asia/Shanghai")
        seen.add(chart.transmissions.method)

    assert seen <= {"贼克", "比用", "涉害", "遥克", "昴星", "别责", "八专", "伏吟", "返吟"}
    assert seen


def test_fuyin_chart_uses_fuyin_method_when_heaven_equals_earth():
    chart = build_chart("2026-05-21 15:30", timezone="Asia/Shanghai")

    if all(earth == heaven for earth, heaven in chart.heaven_plate.items()):
        assert chart.transmissions.method == "伏吟"
        assert chart.transmissions.items[0] is not None


def test_fanyin_with_ke_uses_opposite_as_middle_and_first_upper_as_last():
    chart = build_chart("2026-05-01 05:30", timezone="Asia/Shanghai")

    assert chart.transmissions.method == "比用"
    assert chart.transmissions.items == ("巳", "亥", "亥")
    assert "返吟" in chart.transmissions.note


def test_fanyin_without_ke_uses_jinglan_she():
    chart = build_chart("2026-05-03 05:30", timezone="Asia/Shanghai")

    assert chart.transmissions.status == "complete"
    assert chart.transmissions.method == "返吟"
    assert chart.transmissions.items == ("亥", "未", "丑")
    assert "驿马" in chart.transmissions.note


def test_bazhuan_without_ke_is_used_before_bieze_or_yaoke():
    chart = build_chart("2026-02-02 01:30", timezone="Asia/Shanghai")

    assert chart.calendar.day_gz == "丁未"
    assert chart.transmissions.status == "complete"
    assert chart.transmissions.method == "八专"
    assert chart.transmissions.items == ("卯", "午", "午")


def test_chart_exposes_lesson_bodies_and_brief_analysis():
    chart = build_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai")

    assert chart.lesson_bodies[0]["name"] == "遥克课"
    assert chart.lesson_bodies[0]["category"] == "九宗门"
    assert chart.brief_analysis.startswith("课体：遥克课")


def test_chart_exposes_common_spirit_sha():
    chart = build_chart("2026-05-26 11:58:00", timezone="Asia/Shanghai")

    assert chart.calendar.day_gz == "庚子"
    assert chart.spirit_sha["day_based"]["日德"]["branch"] == "申"
    assert chart.spirit_sha["day_based"]["日禄"]["branch"] == "申"
    assert chart.spirit_sha["day_based"]["日鬼"]["branch"] == "午"
    assert chart.spirit_sha["day_based"]["日官"]["branch"] == "巳"
    assert chart.spirit_sha["branch_based"]["驿马"]["branch"] == "寅"
    assert chart.spirit_sha["branch_based"]["桃花"]["branch"] == "酉"
    assert chart.spirit_sha["branch_based"]["华盖"]["branch"] == "辰"
    assert chart.spirit_sha["year_based"]["太岁"]["branch"] == "午"
    assert chart.spirit_sha["year_based"]["岁破"]["branch"] == "子"
    assert chart.spirit_sha["month_based"]["月建"]["branch"] == "巳"
    assert chart.spirit_sha["month_based"]["月破"]["branch"] == "亥"
    assert chart.spirit_sha["month_based"]["天马"]["branch"] == "子"
    assert chart.spirit_sha["xun_based"]["丁马"]["branch"] == "酉"


def test_tianma_follows_month_branch_six_yang_sequence():
    assert build_chart("2026-02-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "午"
    assert build_chart("2026-03-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "申"
    assert build_chart("2026-04-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "戌"
    assert build_chart("2026-05-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "子"
    assert build_chart("2026-06-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "寅"
    assert build_chart("2026-07-10 12:00", timezone="Asia/Shanghai").spirit_sha["month_based"]["天马"]["branch"] == "辰"


def test_spirit_sha_active_hits_include_transmissions_and_four_lessons():
    chart = build_chart("2026-05-26 11:58:00", timezone="Asia/Shanghai")

    active = chart.spirit_sha["active"]
    names = {(item["name"], item["branch"], item["location"]) for item in active}

    assert ("太岁", "午", "三传中传") in names
    assert ("日德", "申", "三传末传") in names
    assert ("日禄", "申", "三传末传") in names
    assert ("驿马", "寅", "四课三课上") in names
    assert ("岁破", "子", "日支") in names
    assert ("天马", "子", "日支") in names


def test_transmission_details_include_xun_dun_and_season_state():
    chart = build_chart("2026-05-26 11:58:00", timezone="Asia/Shanghai")

    assert chart.calendar.day_gz == "庚子"
    assert chart.xun_dun["xun_start"] == "甲午"
    assert chart.xun_dun["branch_to_stem"]["午"] == "甲"
    assert chart.xun_dun["branch_to_stem"]["申"] == "丙"
    assert chart.xun_dun["branch_to_stem"]["辰"] is None
    assert [item["dun_gan"] for item in chart.transmission_details] == [None, "甲", "丙"]
    assert [item["season_state"] for item in chart.transmission_details] == ["相", "旺", "死"]


def test_spirit_sha_active_hits_include_season_state():
    chart = build_chart("2026-05-26 11:58:00", timezone="Asia/Shanghai")

    day_ghost = next(
        item for item in chart.spirit_sha["active"]
        if item["name"] == "日鬼" and item["location"] == "三传中传"
    )

    assert day_ghost["branch"] == "午"
    assert day_ghost["season_state"] == "旺"


def test_divination_extends_spirit_sha_hits_with_life_and_traveling_year():
    divination = build_divination(
        "2026-05-26 11:58:00",
        timezone="Asia/Shanghai",
        mode="time",
        gender="男",
        question="测试行年神煞",
        birth_year=2008,
    )

    payload = divination.to_dict()
    names = {
        (item["name"], item["branch"], item["location"])
        for item in payload["spirit_sha"]["active"]
    }

    assert payload["querent"]["life_branch"] == "子"
    assert payload["querent"]["traveling_year"] == "申"
    assert ("日德", "申", "行年") in names
    assert ("日禄", "申", "行年") in names


def test_divination_extra_positions_can_activate_xunding_dingma():
    divination = build_divination(
        "2026-05-26 11:58:00",
        timezone="Asia/Shanghai",
        mode="time",
        gender="男",
        question="测试丁马",
        birth_year=2005,
    )

    payload = divination.to_dict()
    names = {
        (item["name"], item["branch"], item["location"])
        for item in payload["spirit_sha"]["active"]
    }

    assert payload["spirit_sha"]["xun_based"]["丁马"]["branch"] == "酉"
    assert payload["querent"]["life_branch"] == "酉"
    assert ("丁马", "酉", "本命") in names


def test_live_hour_keeps_date_and_month_general_but_replaces_hour_branch():
    normal = build_chart("2026-05-26 10:14:15", timezone="Asia/Shanghai")
    live = build_divination(
        "2026-05-26 10:14:15",
        timezone="Asia/Shanghai",
        mode="live-hour",
        hour_branch="子",
        gender="男",
        question="测试活时",
    )

    assert live.chart.calendar.day_gz == normal.calendar.day_gz
    assert live.chart.month_general == normal.month_general
    assert live.chart.calendar.hour_branch == "子"
    assert live.chart.calendar.hour_gz == "丙子"
    assert live.divination["mode"] == "live-hour"
    assert live.divination["source_hour_branch"] == "子"


def test_number_divination_maps_reported_number_to_hour_branch():
    assert number_to_hour_branch(1) == "子"
    assert number_to_hour_branch(12) == "亥"
    assert number_to_hour_branch(13) == "子"
    assert number_to_hour_branch(20) == "未"
    assert number_to_hour_branch(24) == "亥"

    divination = build_divination(
        "2026-05-26 10:14:15",
        timezone="Asia/Shanghai",
        mode="number",
        number=20,
        gender="女",
        question="测试报数",
    )

    assert divination.chart.calendar.hour_branch == "未"
    assert divination.divination["number"] == 20
    assert divination.divination["source_hour_branch"] == "未"


def test_querent_life_year_and_traveling_year_follow_local_rule():
    querent = calculate_querent(
        gender="男",
        question="测试年命",
        chart_year=2006,
        birth_year=1970,
    )

    assert querent["gender"] == "男"
    assert querent["birth_year_ganzhi"] == "庚戌"
    assert querent["life_branch"] == "戌"
    assert querent["virtual_age"] == 37
    assert querent["traveling_year"] == "寅"

    female = calculate_querent(
        gender="女",
        question="测试年命",
        chart_year=2006,
        birth_year=1970,
    )

    assert female["virtual_age"] == 37
    assert female["traveling_year"] == "申"


def test_divination_requires_gender_and_question_for_agent_input():
    try:
        build_divination("2026-05-26 10:14:15", mode="time", gender="", question=" ")
    except ValueError as exc:
        assert "性别" in str(exc)
        assert "所问事" in str(exc)
    else:
        raise AssertionError("missing required fields should fail")
