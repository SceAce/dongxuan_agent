from __future__ import annotations

CLASHES = {
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

TIMING_ROLES = {"useful_god", "original_spirit", "avoiding_spirit", "enemy_spirit"}


def build_timing_analysis(
    derived_lines: list[dict],
    combination_analysis: dict,
    flying_hidden_analysis: dict,
    advance_retreat_analysis: dict,
) -> dict:
    candidates = []
    candidates.extend(_void_candidates(derived_lines))
    candidates.extend(_moving_candidates(derived_lines))
    candidates.extend(_combination_candidates(combination_analysis))
    candidates.extend(_flying_hidden_candidates(flying_hidden_analysis))
    candidates.extend(_advance_retreat_candidates(advance_retreat_analysis))
    return {
        "enabled": True,
        "scope": "应期只输出地支候选触发点，不输出公历日期。",
        "candidates": _dedupe(candidates),
        "unresolved": ["当前不换算公历日期。"],
    }


def _void_candidates(derived_lines: list[dict]) -> list[dict]:
    result = []
    for line in derived_lines:
        if line["spirit_role"] not in {"useful_god", "original_spirit"} or not line["void_state"]["is_void"]:
            continue
        result.append(_candidate(line["branch"], "value_when_filled", "void_state", line))
        result.append(_candidate(CLASHES[line["branch"]], "clash_void", "void_state", line))
    return result


def _moving_candidates(derived_lines: list[dict]) -> list[dict]:
    result = []
    for line in derived_lines:
        if not line["moving"] or line["spirit_role"] not in TIMING_ROLES:
            continue
        changed = line.get("changed_line_state")
        if changed:
            result.append(_candidate(changed["changed_branch"], "changed_branch_value", "relations.moving_effects", line))
    return result


def _combination_candidates(combination_analysis: dict) -> list[dict]:
    result = []
    for group in combination_analysis["groups"]:
        if group["type"] == "full_three_combination":
            continue
        for branch in group["missing_branches"]:
            result.append(
                {
                    "branch": branch,
                    "basis": "combination_completion",
                    "source": "combination_analysis",
                    "line": None,
                    "spirit_role": None,
                    "confidence": "low",
                    "caution": "候选应期需结合现实周期，不等于确定日期。",
                }
            )
    return result


def _flying_hidden_candidates(flying_hidden_analysis: dict) -> list[dict]:
    result = []
    for item in flying_hidden_analysis["hidden_useful_gods"]:
        result.append(
            {
                "branch": item["hidden_branch"],
                "basis": "hidden_spirit_value",
                "source": "flying_hidden_analysis",
                "line": item["position"],
                "spirit_role": item["hidden_role_impact"],
                "confidence": "medium",
                "caution": "候选应期需结合现实周期，不等于确定日期。",
            }
        )
        result.append(
            {
                "branch": CLASHES[item["flying_branch"]],
                "basis": "clash_flying",
                "source": "flying_hidden_analysis",
                "line": item["position"],
                "spirit_role": item["hidden_role_impact"],
                "confidence": "low",
                "caution": "候选应期需结合现实周期，不等于确定日期。",
            }
        )
    return result


def _advance_retreat_candidates(advance_retreat_analysis: dict) -> list[dict]:
    result = []
    for item in advance_retreat_analysis["by_moving_line"]:
        if item["change_type"] == "none":
            continue
        result.append(
            {
                "branch": item["to_branch"],
                "basis": "advance_retreat_value",
                "source": "advance_retreat_analysis",
                "line": item["position"],
                "spirit_role": item["spirit_role"],
                "confidence": "medium",
                "caution": "候选应期需结合现实周期，不等于确定日期。",
            }
        )
    return result


def _candidate(branch: str, basis: str, source: str, line: dict) -> dict:
    return {
        "branch": branch,
        "basis": basis,
        "source": source,
        "line": line["position"],
        "spirit_role": line["spirit_role"],
        "confidence": "medium",
        "caution": "候选应期需结合现实周期，不等于确定日期。",
    }


def _dedupe(candidates: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for item in candidates:
        key = (item["branch"], item["basis"], item["source"], item["line"])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
