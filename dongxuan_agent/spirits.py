from __future__ import annotations

from .calendar_engine import CalendarInfo
from .constants import (
    BRANCHES,
    BRANCH_ELEMENTS,
    BRANCH_OPPOSITE,
    BRANCH_YINYANG,
    CONTROLLING,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
    STEM_YINYANG,
)
from .season import season_state
from .transmissions import Transmissions


DAY_VIRTUE = {
    "甲": "寅", "乙": "申",
    "丙": "巳", "丁": "亥",
    "戊": "巳", "己": "寅",
    "庚": "申", "辛": "巳",
    "壬": "亥", "癸": "巳",
}

DAY_LU = {
    "甲": "寅", "乙": "卯",
    "丙": "巳", "丁": "午",
    "戊": "巳", "己": "午",
    "庚": "申", "辛": "酉",
    "壬": "亥", "癸": "子",
}

THREE_HARMONY_SPIRITS = {
    ("寅", "午", "戌"): {"驿马": "申", "桃花": "卯", "华盖": "戌"},
    ("申", "子", "辰"): {"驿马": "寅", "桃花": "酉", "华盖": "辰"},
    ("巳", "酉", "丑"): {"驿马": "亥", "桃花": "午", "华盖": "丑"},
    ("亥", "卯", "未"): {"驿马": "巳", "桃花": "子", "华盖": "未"},
}


def build_spirit_sha(
    calendar: CalendarInfo,
    four_lessons: tuple,
    transmissions: Transmissions,
    extra_positions: tuple[dict[str, str], ...] = (),
    xun_dun: dict | None = None,
) -> dict:
    day_stem = calendar.day_gz[0]
    day_branch = calendar.day_gz[1]
    year_branch = calendar.year_gz[1]
    month_branch = calendar.month_gz[1]
    xun_dun = xun_dun or {}
    all_spirits = {
        "day_based": _day_based(day_stem),
        "branch_based": _branch_based(day_branch),
        "year_based": {
            "太岁": _spirit("太岁", year_branch, "岁君，一年主气。"),
            "岁破": _spirit("岁破", BRANCH_OPPOSITE[year_branch], "太岁对冲，主冲破变动。"),
        },
        "month_based": {
            "月建": _spirit("月建", month_branch, "月令主气。"),
            "月破": _spirit("月破", BRANCH_OPPOSITE[month_branch], "月建对冲，主月内冲破。"),
            "天马": _spirit("天马", _tianma(month_branch), "三马之一，主迁移更改、远行出征、火速动象。"),
        },
        "xun_based": {
            "丁马": _spirit("丁马", _dingma(xun_dun), "又名旬丁、六丁，三马之一，主动摇、变化、出行、灯火动摇。"),
        },
    }
    flat = _flatten(all_spirits)
    all_spirits["active"] = _active_hits(flat, calendar, four_lessons, transmissions, extra_positions)
    return all_spirits


def _day_based(day_stem: str) -> dict[str, dict[str, str]]:
    return {
        "日德": _spirit("日德", DAY_VIRTUE[day_stem], "德可化鬼，临日入传为转凶助吉之象。"),
        "日禄": _spirit("日禄", DAY_LU[day_stem], "食禄、俸禄、资用之象。"),
        "日鬼": _spirit("日鬼", _day_ghost_or_officer(day_stem, same_yinyang=True), "克日且阴阳同类，主压力、病讼、风险。"),
        "日官": _spirit("日官", _day_ghost_or_officer(day_stem, same_yinyang=False), "克日且阴阳异类，功名职位亦可取象。"),
    }


def _day_ghost_or_officer(day_stem: str, *, same_yinyang: bool) -> str:
    day_element = STEM_ELEMENTS[day_stem]
    day_yinyang = STEM_YINYANG[day_stem]
    candidates = [
        branch
        for branch in BRANCHES
        if CONTROLLING[BRANCH_ELEMENTS[branch]] == day_element
        and (BRANCH_YINYANG[branch] == day_yinyang) == same_yinyang
    ]
    return "、".join(candidates)


def _branch_based(branch: str) -> dict[str, dict[str, str]]:
    rules = _three_harmony_rule(branch)
    return {
        "驿马": _spirit("驿马", rules["驿马"], "动象，迁移、奔走、变化、远信。"),
        "桃花": _spirit("桃花", rules["桃花"], "又名咸池，主情欲、人缘、外饰、社交。"),
        "华盖": _spirit("华盖", rules["华盖"], "主孤高、技艺、学术、宗教、遮蔽。"),
    }


def _three_harmony_rule(branch: str) -> dict[str, str]:
    for group, rule in THREE_HARMONY_SPIRITS.items():
        if branch in group:
            return rule
    raise ValueError(branch)


def _tianma(month_branch: str) -> str:
    return {
        "寅": "午", "申": "午",
        "卯": "申", "酉": "申",
        "辰": "戌", "戌": "戌",
        "巳": "子", "亥": "子",
        "午": "寅", "子": "寅",
        "未": "辰", "丑": "辰",
    }[month_branch]


def _dingma(xun_dun: dict) -> str:
    branch_to_stem = xun_dun.get("branch_to_stem", {})
    for branch in BRANCHES:
        if branch_to_stem.get(branch) == "丁":
            return branch
    raise ValueError("xun_dun does not contain 丁")


def _spirit(name: str, branch: str, meaning: str) -> dict[str, str]:
    return {
        "name": name,
        "branch": branch,
        "meaning": meaning,
    }


def _flatten(grouped: dict[str, dict[str, dict[str, str]]]) -> list[dict[str, str]]:
    result = []
    for category, spirits in grouped.items():
        for spirit in spirits.values():
            result.append({**spirit, "category": category})
    return result


def _active_hits(
    spirits: list[dict[str, str]],
    calendar: CalendarInfo,
    four_lessons: tuple,
    transmissions: Transmissions,
    extra_positions: tuple[dict[str, str], ...],
) -> list[dict[str, str]]:
    positions = _positions(calendar, four_lessons, transmissions, extra_positions)
    active = []
    for spirit in spirits:
        branches = spirit["branch"].split("、")
        for position in positions:
            if position["branch"] in branches:
                active.append({
                    **spirit,
                    **position,
                    "season_state": season_state(position["branch"], calendar.month_gz[1]),
                })
    return active


def _positions(
    calendar: CalendarInfo,
    four_lessons: tuple,
    transmissions: Transmissions,
    extra_positions: tuple[dict[str, str], ...],
) -> list[dict[str, str]]:
    positions = [
        {"location": "日支", "branch": calendar.day_gz[1]},
        {"location": "太岁", "branch": calendar.year_gz[1]},
        {"location": "月建", "branch": calendar.month_gz[1]},
    ]
    for lesson in four_lessons:
        if lesson.lower in BRANCHES:
            positions.append({"location": f"四课{lesson.name}下", "branch": lesson.lower})
        positions.append({"location": f"四课{lesson.name}上", "branch": lesson.upper})
    for index, branch in enumerate(transmissions.items):
        if branch is None:
            continue
        positions.append({"location": ("三传初传", "三传中传", "三传末传")[index], "branch": branch})
    positions.extend(extra_positions)
    return positions
