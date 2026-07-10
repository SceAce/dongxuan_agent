from __future__ import annotations

from .relations import CONTROLLING, GENERATING

BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

BASE_STRENGTH = {
    "旺": 2,
    "相": 1,
    "休": 0,
    "囚": -1,
    "死": -2,
}


def seasonal_state(line_element: str, month_branch: str) -> str:
    month_element = BRANCH_ELEMENTS[month_branch]
    if line_element == month_element:
        return "旺"
    if GENERATING[month_element] == line_element:
        return "相"
    if GENERATING[line_element] == month_element:
        return "休"
    if CONTROLLING[line_element] == month_element:
        return "囚"
    if CONTROLLING[month_element] == line_element:
        return "死"
    raise ValueError(f"无法推导旺相休囚死：{line_element=} {month_branch=}")


def effective_strength(seasonal: str, support_factors: list[str], weakening_factors: list[str]) -> str:
    score = BASE_STRENGTH[seasonal] + len(support_factors) - len(weakening_factors)
    if score >= 4:
        return "very_strong"
    if score >= 1:
        return "strong"
    if score == 0:
        return "balanced"
    if score <= -3:
        return "very_weak"
    return "weak"


def extreme_state(seasonal: str, support_factors: list[str], weakening_factors: list[str]) -> str:
    if seasonal in {"旺", "相"} and len(support_factors) >= 2 and not weakening_factors:
        return "over_strong"
    if seasonal in {"囚", "死"} and len(weakening_factors) >= 2 and not support_factors:
        return "over_weak"
    return "none"
