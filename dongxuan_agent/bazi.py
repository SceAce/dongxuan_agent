from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import sxtwl

from .calendar_engine import CalendarInfo, get_calendar_info, hour_gz_by_branch, parse_datetime, xunkong_for_day
from .constants import (
    BRANCH_OPPOSITE,
    BRANCH_PUNISH,
    BRANCHES,
    CONTROLLING,
    GENERATING,
    STEM_ELEMENTS,
    STEM_YINYANG,
    JIAZI,
)


HIDDEN_STEMS = {
    "子": ("癸",),
    "丑": ("己", "癸", "辛"),
    "寅": ("甲", "丙", "戊"),
    "卯": ("乙",),
    "辰": ("戊", "乙", "癸"),
    "巳": ("丙", "戊", "庚"),
    "午": ("丁", "己"),
    "未": ("己", "丁", "乙"),
    "申": ("庚", "壬", "戊"),
    "酉": ("辛",),
    "戌": ("戊", "辛", "丁"),
    "亥": ("壬", "甲"),
}

BRANCH_COMBINE = {
    frozenset(("子", "丑")): "土",
    frozenset(("寅", "亥")): "木",
    frozenset(("卯", "戌")): "火",
    frozenset(("辰", "酉")): "金",
    frozenset(("巳", "申")): "水",
    frozenset(("午", "未")): "土",
}

BRANCH_HARM = {
    frozenset(("子", "未")),
    frozenset(("丑", "午")),
    frozenset(("寅", "巳")),
    frozenset(("卯", "辰")),
    frozenset(("申", "亥")),
    frozenset(("酉", "戌")),
}


@dataclass(frozen=True)
class BaziChart:
    calendar: CalendarInfo
    gender: str | None
    pillars: tuple[dict, dict, dict, dict]
    branch_relationships: tuple[dict, ...]
    time_adjustment: dict
    time_rules: dict
    luck: dict | None

    def to_dict(self) -> dict:
        return {
            "calendar": {
                "datetime": self.calendar.dt.isoformat(),
                "timezone": self.calendar.timezone,
                "year_gz": self.calendar.year_gz,
                "month_gz": self.calendar.month_gz,
                "day_gz": self.calendar.day_gz,
                "hour_gz": self.calendar.hour_gz,
            },
            "gender": self.gender,
            "day_master": self.calendar.day_gz[0],
            "time_adjustment": self.time_adjustment,
            "time_rules": self.time_rules,
            "pillars": list(self.pillars),
            "branch_relationships": list(self.branch_relationships),
            "luck": self.luck,
            "xunkong": list(self.calendar.xunkong),
            "uncertainty": [
                "八字排盘 V2 支持经度真太阳时近似校正、早晚子时 split/whole 规则、大运顺逆与三天一岁起运。",
                "真太阳时 V2 仅按经度相对时区中央经线校正，未加入均时差；出生地经度缺省时不启用。",
                "八字 V2 只封装排盘字段，不做旺衰、格局、用神、流年断语。",
            ],
        }


def build_bazi_chart(
    value,
    *,
    timezone: str = "Asia/Shanghai",
    gender: str | None = None,
    longitude: float | None = None,
    zi_hour_rule: str = "whole",
) -> BaziChart:
    adjusted_value, time_adjustment = _adjust_time(value, timezone, longitude)
    calendar = _bazi_calendar(adjusted_value, timezone, zi_hour_rule)
    day_master = calendar.day_gz[0]
    pillar_values = (
        ("年柱", calendar.year_gz),
        ("月柱", calendar.month_gz),
        ("日柱", calendar.day_gz),
        ("时柱", calendar.hour_gz),
    )
    pillars = tuple(_pillar(name, gz, day_master) for name, gz in pillar_values)
    return BaziChart(
        calendar=calendar,
        gender=gender,
        pillars=pillars,  # type: ignore[arg-type]
        branch_relationships=tuple(_branch_relationships([item[1][1] for item in pillar_values])),
        time_adjustment=time_adjustment,
        time_rules={
            "zi_hour_rule": zi_hour_rule,
            "zi_hour_rule_note": "whole 为 23:00-00:59 同属当日子时；split 为 23:00-23:59 晚子换次日，00:00-00:59 早子属当日。",
        },
        luck=_build_luck(calendar, gender),
    )


def _adjust_time(value, timezone: str, longitude: float | None) -> tuple[datetime, dict]:
    dt = parse_datetime(value, timezone)
    if longitude is None:
        return dt, {
            "mode": "standard",
            "original_datetime": dt.isoformat(),
            "adjusted_datetime": dt.isoformat(),
            "longitude": None,
            "offset_minutes": 0,
        }
    central_longitude = _timezone_central_longitude(dt)
    offset_minutes = round((longitude - central_longitude) * 4)
    adjusted = dt + timedelta(minutes=offset_minutes)
    return adjusted, {
        "mode": "true_solar",
        "original_datetime": dt.isoformat(),
        "adjusted_datetime": adjusted.isoformat(),
        "longitude": longitude,
        "central_longitude": central_longitude,
        "offset_minutes": offset_minutes,
        "rule": "经度每差 1 度折 4 分钟；V2 未加入均时差。",
    }


def _timezone_central_longitude(dt: datetime) -> float:
    offset = dt.utcoffset()
    if offset is None:
        return 120.0
    return offset.total_seconds() / 3600 * 15


def _bazi_calendar(value: datetime, timezone: str, zi_hour_rule: str) -> CalendarInfo:
    if zi_hour_rule not in {"whole", "split"}:
        raise ValueError("zi_hour_rule 必须为 whole 或 split")
    if zi_hour_rule == "whole":
        return get_calendar_info(value, timezone)
    dt = parse_datetime(value, timezone)
    day_dt = dt + timedelta(days=1) if dt.hour == 23 else dt
    base = get_calendar_info(day_dt, timezone)
    hour_branch = BRANCHES[((dt.hour + 1) // 2) % 12]
    hour_gz = hour_gz_by_branch(base.day_gz[0], hour_branch)
    return CalendarInfo(
        dt=dt,
        timezone=base.timezone,
        year_gz=base.year_gz,
        month_gz=base.month_gz,
        day_gz=base.day_gz,
        hour_gz=hour_gz,
        hour_branch=hour_branch,
        xunkong=xunkong_for_day(base.day_gz),
        month_general=base.month_general,
    )


def ten_god(day_master: str, other_stem: str) -> str:
    if day_master == other_stem:
        return "日主"
    day_element = STEM_ELEMENTS[day_master]
    other_element = STEM_ELEMENTS[other_stem]
    same_yinyang = STEM_YINYANG[day_master] == STEM_YINYANG[other_stem]
    if other_element == day_element:
        return "比肩" if same_yinyang else "劫财"
    if GENERATING[other_element] == day_element:
        return "偏印" if same_yinyang else "正印"
    if GENERATING[day_element] == other_element:
        return "食神" if same_yinyang else "伤官"
    if CONTROLLING[day_element] == other_element:
        return "偏财" if same_yinyang else "正财"
    if CONTROLLING[other_element] == day_element:
        return "七杀" if same_yinyang else "正官"
    raise ValueError(f"cannot derive ten god for {day_master=} {other_stem=}")


def _pillar(name: str, gz: str, day_master: str) -> dict:
    stem, branch = gz[0], gz[1]
    return {
        "name": name,
        "ganzhi": gz,
        "stem": stem,
        "branch": branch,
        "stem_ten_god": "日主" if name == "日柱" else ten_god(day_master, stem),
        "hidden_stems": [
            {"stem": hidden, "ten_god": ten_god(day_master, hidden)}
            for hidden in HIDDEN_STEMS[branch]
        ],
    }


def _branch_relationships(branches: list[str]) -> list[dict]:
    result = []
    for left_index, left in enumerate(branches):
        for right in branches[left_index + 1:]:
            pair = _branch_pair(left, right)
            if BRANCH_OPPOSITE[left] == right:
                result.append({"type": "冲", "branches": pair})
            combine_element = BRANCH_COMBINE.get(frozenset((left, right)))
            if combine_element:
                result.append({"type": "合", "branches": pair, "element": combine_element})
            if frozenset((left, right)) in BRANCH_HARM:
                result.append({"type": "害", "branches": pair})
            if BRANCH_PUNISH.get(left) == right:
                result.append({"type": "刑", "branches": pair})
    for branch in BRANCHES:
        if branches.count(branch) >= 2 and BRANCH_PUNISH.get(branch) == branch:
            result.append({"type": "自刑", "branches": branch + branch})
    return result


def _branch_pair(left: str, right: str) -> str:
    return "".join(sorted((left, right), key=BRANCHES.index))


def _build_luck(calendar: CalendarInfo, gender: str | None) -> dict | None:
    if gender not in {"男", "女"}:
        return None
    direction = _luck_direction(calendar.year_gz[0], gender)
    boundary = _luck_boundary(calendar.dt, direction)
    delta = boundary - calendar.dt if direction == "顺" else calendar.dt - boundary
    total_days = delta.total_seconds() / 86400
    start_age_years = total_days / 3
    start_age_months = start_age_years * 12
    return {
        "direction": direction,
        "rule": "阳男阴女顺行，阴男阳女逆行；起运按出生时刻至顺/逆最近节气，三天折一岁。",
        "boundary": boundary.isoformat(),
        "start": {
            "days_to_boundary": round(total_days, 6),
            "start_age_years": round(start_age_years, 3),
            "start_age_months": round(start_age_months, 2),
        },
        "cycles": _luck_cycles(calendar.month_gz, direction, start_age_years),
    }


def _luck_direction(year_stem: str, gender: str) -> str:
    is_yang_year = STEM_YINYANG[year_stem] == "阳"
    if (gender == "男" and is_yang_year) or (gender == "女" and not is_yang_year):
        return "顺"
    return "逆"


def _luck_boundary(dt: datetime, direction: str) -> datetime:
    candidates = []
    for year in (dt.year - 1, dt.year, dt.year + 1):
        for info in sxtwl.getJieQiByYear(year):
            boundary = _jieqi_datetime(info.jd, dt.tzinfo)
            candidates.append(boundary)
    if direction == "顺":
        return min(item for item in candidates if item > dt)
    return max(item for item in candidates if item < dt)


def _jieqi_datetime(jd, tzinfo) -> datetime:
    t = sxtwl.JD2DD(jd)
    return datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(t.m), int(t.s), tzinfo=tzinfo or ZoneInfo("Asia/Shanghai"))


def _luck_cycles(month_gz: str, direction: str, start_age_years: float) -> list[dict]:
    month_index = JIAZI.index(month_gz)
    step = 1 if direction == "顺" else -1
    cycles = []
    for index in range(1, 9):
        gz = JIAZI[(month_index + step * index) % 60]
        start_age = start_age_years + (index - 1) * 10
        cycles.append({
            "index": index,
            "ganzhi": gz,
            "start_age_years": round(start_age, 3),
            "end_age_years": round(start_age + 10, 3),
        })
    return cycles
