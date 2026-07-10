from __future__ import annotations

BRANCH_OPPOSITE = {
    "子": "午",
    "丑": "未",
    "寅": "申",
    "卯": "酉",
    "辰": "戌",
    "巳": "亥",
    "午": "子",
    "未": "丑",
    "申": "寅",
    "酉": "卯",
    "戌": "辰",
    "亥": "巳",
}

BRANCH_COMBINES = {
    frozenset(("子", "丑")),
    frozenset(("寅", "亥")),
    frozenset(("卯", "戌")),
    frozenset(("辰", "酉")),
    frozenset(("巳", "申")),
    frozenset(("午", "未")),
}

GENERATING = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

CONTROLLING = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}


def branch_relation(left_branch: str, right_branch: str) -> str:
    if left_branch == right_branch:
        return "same"
    if BRANCH_OPPOSITE[left_branch] == right_branch:
        return "clash"
    if frozenset((left_branch, right_branch)) in BRANCH_COMBINES:
        return "combine"
    return "none"


def element_relation(actor_element: str, target_element: str) -> str:
    if actor_element == target_element:
        return "same"
    if GENERATING[actor_element] == target_element:
        return "generates"
    if GENERATING[target_element] == actor_element:
        return "generated_by"
    if CONTROLLING[actor_element] == target_element:
        return "controls"
    if CONTROLLING[target_element] == actor_element:
        return "controlled_by"
    return "none"


def return_relation_label(actor_element: str, changed_element: str) -> str:
    relation = element_relation(changed_element, actor_element)
    if relation == "generates":
        return "回头生"
    if relation == "controls":
        return "回头克"
    if relation == "same":
        return "比和"
    actor_to_changed = element_relation(actor_element, changed_element)
    if actor_to_changed == "generates":
        return "泄气"
    if actor_to_changed == "controls":
        return "耗气"
    return "无直接作用"
