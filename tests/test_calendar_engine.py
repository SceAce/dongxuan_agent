from datetime import datetime
from zoneinfo import ZoneInfo

from dongxuan_agent.calendar_engine import (
    CalendarInfo,
    get_calendar_info,
    month_general,
    parse_datetime,
    xunkong_for_day,
)


def test_parse_datetime_attaches_named_timezone():
    parsed = parse_datetime("2026-05-25 12:30", "Asia/Shanghai")

    assert parsed == datetime(2026, 5, 25, 12, 30, tzinfo=ZoneInfo("Asia/Shanghai"))


def test_calendar_info_contains_ganzhi_and_hour_branch():
    info = get_calendar_info("2026-05-25 12:30", "Asia/Shanghai")

    assert isinstance(info, CalendarInfo)
    assert len(info.year_gz) == 2
    assert len(info.month_gz) == 2
    assert len(info.day_gz) == 2
    assert len(info.hour_gz) == 2
    assert info.hour_branch == "午"
    assert info.timezone == "Asia/Shanghai"


def test_hour_ganzhi_uses_liushu_dun_for_ji_day():
    info = get_calendar_info("2026-05-25 23:43:24", "Asia/Shanghai")

    assert info.day_gz == "己亥"
    assert info.hour_gz == "甲子"


def test_xunkong_for_known_jiazi_day():
    assert xunkong_for_day("甲子") == ("戌", "亥")


def test_month_general_returns_branch_name():
    general = month_general("2026-05-25 12:30", "Asia/Shanghai")

    assert general in "子丑寅卯辰巳午未申酉戌亥"


def test_month_general_changes_on_zhongqi_boundary():
    before_xiaoman = month_general("2026-05-21 08:00", "Asia/Shanghai")
    after_xiaoman = month_general("2026-05-21 09:00", "Asia/Shanghai")

    assert before_xiaoman == "酉"
    assert after_xiaoman == "申"
