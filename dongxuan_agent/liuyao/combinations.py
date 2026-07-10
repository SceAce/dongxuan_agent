from __future__ import annotations

THREE_COMBINATIONS = {
    ("申", "子", "辰"): "水",
    ("亥", "卯", "未"): "木",
    ("寅", "午", "戌"): "火",
    ("巳", "酉", "丑"): "金",
}


def build_combination_analysis(derived_lines: list[dict], spirit_role_analysis: dict, calendar: dict) -> dict:
    groups = []
    branch_lines: dict[str, list[int]] = {}
    for line in derived_lines:
        branch_lines.setdefault(line["branch"], []).append(line["position"])

    for branches, element in THREE_COMBINATIONS.items():
        present = [branch for branch in branches if branch in branch_lines]
        if len(present) >= 2:
            groups.append(_group("full_three_combination" if len(present) == 3 else "half_combination", branches, present, element, branch_lines, [], spirit_role_analysis))
        elif len(present) == 1:
            external = [branch for branch in (calendar["month_branch"], calendar["day_branch"]) if branch in branches and branch not in present]
            if external:
                groups.append(_group("pending_combination", branches, present, element, branch_lines, external, spirit_role_analysis))

    return {
        "enabled": True,
        "scope": "三合只修正合力方向，不替代用神选择。",
        "groups": groups,
    }


def completion_factors(combination_analysis: dict) -> dict:
    supporting = []
    blocking = []
    mixed = []
    for group in combination_analysis["groups"]:
        factor = {
            "type": "combination_role_impact",
            "line_positions": group["line_positions"],
            "element": group["element"],
            "role_impact": group["role_impact"],
            "summary": group["reason"],
        }
        if group["role_impact"] in {"supports_useful_god", "supports_original_spirit"}:
            supporting.append(factor)
        elif group["role_impact"] in {"supports_avoiding_spirit", "supports_enemy_spirit"}:
            blocking.append(factor)
        else:
            mixed.append(factor)
    return {"supporting_factors": supporting, "blocking_factors": blocking, "mixed_factors": mixed}


def _group(
    group_type: str,
    group_branches: tuple[str, str, str],
    present: list[str],
    element: str,
    branch_lines: dict[str, list[int]],
    external: list[str],
    spirit_role_analysis: dict,
) -> dict:
    line_positions = sorted(position for branch in present for position in branch_lines[branch])
    missing = [branch for branch in group_branches if branch not in present and branch not in external]
    role_impact = _role_impact(element, spirit_role_analysis)
    return {
        "type": group_type,
        "branches": present,
        "missing_branches": missing,
        "element": element,
        "line_positions": line_positions,
        "external_branches": external,
        "role_impact": role_impact,
        "reason": _reason(present, element, role_impact, group_type),
    }


def _role_impact(element: str, spirit_role_analysis: dict) -> str:
    if spirit_role_analysis["status"] != "ready":
        return "mixed"
    role_elements = spirit_role_analysis["role_elements"]
    if element in role_elements["useful_god"]:
        return "supports_useful_god"
    if element in role_elements["original_spirit"]:
        return "supports_original_spirit"
    if element in role_elements["avoiding_spirit"]:
        return "supports_avoiding_spirit"
    if element in role_elements["enemy_spirit"]:
        return "supports_enemy_spirit"
    return "neutral"


def _reason(branches: list[str], element: str, role_impact: str, group_type: str) -> str:
    type_name = {
        "full_three_combination": "三合",
        "half_combination": "半合",
        "pending_combination": "待合",
    }[group_type]
    impact_name = {
        "supports_useful_god": "用神",
        "supports_original_spirit": "原神",
        "supports_avoiding_spirit": "忌神",
        "supports_enemy_spirit": "仇神",
        "neutral": "闲神",
        "mixed": "未定角色",
    }[role_impact]
    return f"{''.join(branches)}{type_name}{element}，{element}为{impact_name}，属角色化合力证据。"
