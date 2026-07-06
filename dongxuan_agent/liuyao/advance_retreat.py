from __future__ import annotations


ADVANCE_PAIRS = {("寅", "卯"), ("巳", "午"), ("申", "酉"), ("亥", "子")}
RETREAT_PAIRS = {(right, left) for left, right in ADVANCE_PAIRS}


def build_advance_retreat_analysis(derived_lines: list[dict], moving_effects: list[dict]) -> dict:
    line_by_position = {line["position"]: line for line in derived_lines}
    by_moving_line = []
    for effect in moving_effects:
        line = line_by_position[effect["actor_position"]]
        changed = effect["changed_line"]
        change_type = _change_type(line["branch"], changed["changed_branch"])
        role_impact = _role_impact(line["spirit_role"], change_type)
        by_moving_line.append(
            {
                "position": line["position"],
                "name": line["name"],
                "spirit_role": line["spirit_role"],
                "change_type": change_type,
                "from_branch": line["branch"],
                "from_element": line["element"],
                "to_branch": changed["changed_branch"],
                "to_element": changed["changed_element"],
                "role_impact": role_impact,
                "reason": _reason(line, changed, change_type, role_impact),
            }
        )
    return {
        "enabled": True,
        "scope": "进退神只用于动爻趋势，不替代用神链。",
        "by_moving_line": by_moving_line,
        "unresolved": [],
    }


def completion_factors(advance_retreat_analysis: dict) -> dict:
    supporting = []
    blocking = []
    mixed = []
    for item in advance_retreat_analysis["by_moving_line"]:
        factor = {
            "type": f"advance_retreat_{item['role_impact']}",
            "line": item["position"],
            "change_type": item["change_type"],
            "spirit_role": item["spirit_role"],
            "summary": item["reason"],
        }
        if item["role_impact"] in {"support_increases", "obstruction_decreases"}:
            supporting.append(factor)
        elif item["role_impact"] in {"support_decreases", "obstruction_increases"}:
            blocking.append(factor)
        else:
            mixed.append(factor)
    return {"supporting_factors": supporting, "blocking_factors": blocking, "mixed_factors": mixed}


def _change_type(from_branch: str, to_branch: str) -> str:
    if (from_branch, to_branch) in ADVANCE_PAIRS:
        return "advance"
    if (from_branch, to_branch) in RETREAT_PAIRS:
        return "retreat"
    return "none"


def _role_impact(spirit_role: str, change_type: str) -> str:
    if change_type == "none":
        return "neutral"
    if spirit_role in {"useful_god", "original_spirit"}:
        return "support_increases" if change_type == "advance" else "support_decreases"
    if spirit_role in {"avoiding_spirit", "enemy_spirit"}:
        return "obstruction_increases" if change_type == "advance" else "obstruction_decreases"
    if spirit_role == "neutral_spirit":
        return "neutral"
    return "ambiguous"


def _reason(line: dict, changed: dict, change_type: str, role_impact: str) -> str:
    change_name = {"advance": "化进", "retreat": "化退", "none": "不成进退"}[change_type]
    impact_name = {
        "support_increases": "支持增强",
        "support_decreases": "支持减弱",
        "obstruction_increases": "阻力增强",
        "obstruction_decreases": "阻力减弱",
        "neutral": "中性",
        "ambiguous": "角色未定",
    }[role_impact]
    return (
        f"{line['name']}{line['branch']}{line['element']}动化"
        f"{changed['changed_branch']}{changed['changed_element']}，{change_name}；"
        f"本爻角色为{line['spirit_role']}，进退影响为{impact_name}。"
    )
