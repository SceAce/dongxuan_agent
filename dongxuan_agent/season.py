from __future__ import annotations

from .constants import BRANCH_ELEMENTS, GENERATING


MONTH_ELEMENT = {
    "寅": "木", "卯": "木", "辰": "土",
    "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土",
    "亥": "水", "子": "水", "丑": "土",
}


def season_state(branch: str, month_branch: str) -> str:
    month_element = MONTH_ELEMENT[month_branch]
    element = BRANCH_ELEMENTS[branch]
    if element == month_element:
        return "旺"
    if GENERATING[month_element] == element:
        return "相"
    if GENERATING[element] == month_element:
        return "休"
    if _controls(month_element, element):
        return "死"
    if _controls(element, month_element):
        return "囚"
    raise ValueError(f"cannot derive season state for {branch=} {month_branch=}")


def _controls(source: str, target: str) -> bool:
    return {
        "木": "土",
        "土": "水",
        "水": "火",
        "火": "金",
        "金": "木",
    }[source] == target
