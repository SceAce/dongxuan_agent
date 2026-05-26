from __future__ import annotations

from dataclasses import dataclass

from .calendar_engine import CalendarInfo, get_calendar_info
from .constants import (
    BRANCH_OPPOSITE,
    BRANCH_PUNISH,
    BRANCHES,
    CONTROLLING,
    GENERATING,
    STEM_ELEMENTS,
    STEM_YINYANG,
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
            "pillars": list(self.pillars),
            "branch_relationships": list(self.branch_relationships),
            "xunkong": list(self.calendar.xunkong),
            "uncertainty": [
                "八字排盘 V1 使用 sxtwl 四柱与六鼠遁时柱；真太阳时、早晚子时、节气边界派别暂未展开。",
                "八字 V1 只封装排盘字段，不做旺衰、格局、用神、大运流年断语。",
            ],
        }


def build_bazi_chart(value, *, timezone: str = "Asia/Shanghai", gender: str | None = None) -> BaziChart:
    calendar = get_calendar_info(value, timezone)
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
