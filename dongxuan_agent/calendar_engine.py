from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import sxtwl

from .constants import BRANCHES, JIAZI, STEMS, ZHONGQI_MONTH_GENERAL


@dataclass(frozen=True)
class CalendarInfo:
    dt: datetime
    timezone: str
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    hour_branch: str
    xunkong: tuple[str, str]
    month_general: str


def parse_datetime(value: str | datetime, timezone: str = "Asia/Shanghai") -> datetime:
    tz = ZoneInfo(timezone)
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)
    normalized = value.strip().replace("T", " ")
    dt = datetime.fromisoformat(normalized)
    return dt.astimezone(tz) if dt.tzinfo else dt.replace(tzinfo=tz)


def _gz_to_text(gz) -> str:
    return STEMS[gz.tg] + BRANCHES[gz.dz]


def _hour_branch(hour: int) -> str:
    return BRANCHES[((hour + 1) // 2) % 12]


def _hour_gz_by_liushu_dun(day_stem: str, hour: int) -> str:
    start_stem_by_day = {
        "甲": "甲", "己": "甲",
        "乙": "丙", "庚": "丙",
        "丙": "戊", "辛": "戊",
        "丁": "庚", "壬": "庚",
        "戊": "壬", "癸": "壬",
    }
    branch = _hour_branch(hour)
    branch_index = BRANCHES.index(branch)
    start_stem_index = STEMS.index(start_stem_by_day[day_stem])
    return STEMS[(start_stem_index + branch_index) % 10] + branch


def hour_gz_by_branch(day_stem: str, hour_branch: str) -> str:
    if hour_branch not in BRANCHES:
        raise ValueError(f"invalid hour branch: {hour_branch}")
    start_stem_by_day = {
        "甲": "甲", "己": "甲",
        "乙": "丙", "庚": "丙",
        "丙": "戊", "辛": "戊",
        "丁": "庚", "壬": "庚",
        "戊": "壬", "癸": "壬",
    }
    branch_index = BRANCHES.index(hour_branch)
    start_stem_index = STEMS.index(start_stem_by_day[day_stem])
    return STEMS[(start_stem_index + branch_index) % 10] + hour_branch


def xunkong_for_day(day_gz: str) -> tuple[str, str]:
    idx = JIAZI.index(day_gz)
    xun_start = (idx // 10) * 10
    used = {JIAZI[(xun_start + i) % 60][1] for i in range(10)}
    empty = [branch for branch in BRANCHES if branch not in used]
    return empty[0], empty[1]


def month_general(value: str | datetime, timezone: str = "Asia/Shanghai") -> str:
    dt = parse_datetime(value, timezone)
    latest = None
    for year in (dt.year - 1, dt.year):
        for info in sxtwl.getJieQiByYear(year):
            if info.jqIndex % 2 != 0:
                continue
            t = sxtwl.JD2DD(info.jd)
            boundary = datetime(
                int(t.Y),
                int(t.M),
                int(t.D),
                int(t.h),
                int(t.m),
                int(t.s),
                tzinfo=ZoneInfo(timezone),
            )
            if boundary <= dt:
                latest = info.jqIndex
    if latest is None:
        latest = 0
    return ZHONGQI_MONTH_GENERAL[latest]


def get_calendar_info(value: str | datetime, timezone: str = "Asia/Shanghai") -> CalendarInfo:
    dt = parse_datetime(value, timezone)
    day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    year_gz = _gz_to_text(day.getYearGZ())
    month_gz = _gz_to_text(day.getMonthGZ())
    day_gz = _gz_to_text(day.getDayGZ())
    hour_gz = _hour_gz_by_liushu_dun(day_gz[0], dt.hour)
    return CalendarInfo(
        dt=dt,
        timezone=timezone,
        year_gz=year_gz,
        month_gz=month_gz,
        day_gz=day_gz,
        hour_gz=hour_gz,
        hour_branch=hour_gz[1],
        xunkong=xunkong_for_day(day_gz),
        month_general=month_general(dt, timezone),
    )


def with_hour_branch(calendar: CalendarInfo, hour_branch: str) -> CalendarInfo:
    hour_gz = hour_gz_by_branch(calendar.day_gz[0], hour_branch)
    return CalendarInfo(
        dt=calendar.dt,
        timezone=calendar.timezone,
        year_gz=calendar.year_gz,
        month_gz=calendar.month_gz,
        day_gz=calendar.day_gz,
        hour_gz=hour_gz,
        hour_branch=hour_branch,
        xunkong=calendar.xunkong,
        month_general=calendar.month_general,
    )
