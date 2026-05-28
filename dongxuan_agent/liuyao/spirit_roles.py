from __future__ import annotations

from .relations import CONTROLLING, GENERATING, element_relation


ROLE_NAMES = {
    "useful_god": "用神",
    "original_spirit": "原神",
    "avoiding_spirit": "忌神",
    "enemy_spirit": "仇神",
    "neutral_spirit": "闲神",
    "unresolved": "未定",
}


def build_spirit_role_analysis(derived_lines: list[dict], useful_god_selection: dict) -> dict:
    result = useful_god_selection["selection_result"]
    status = result["status"]
    main = result["main_useful_god"]
    auxiliaries = list(result["auxiliary_useful_gods"])
    if status in {"ambiguous", "missing"} or main is None:
        _mark_unresolved(derived_lines, "主用神未定，暂不分配原忌仇神。")
        return {
            "status": status,
            "main_useful_god": main,
            "auxiliary_useful_gods": auxiliaries,
            "useful_god_elements": [],
            "role_elements": {},
            "by_line": [],
            "unresolved": ["主用神未定，暂不分配原忌仇神。"],
        }

    useful_lines = [line for line in derived_lines if line["six_relative"] == main]
    useful_elements = sorted({line["element"] for line in useful_lines})
    if not useful_lines:
        _mark_unresolved(derived_lines, "主用神不上卦，飞伏未实现前不补隐藏用神。")
        return {
            "status": "missing",
            "main_useful_god": main,
            "auxiliary_useful_gods": auxiliaries,
            "useful_god_elements": [],
            "role_elements": {},
            "by_line": [],
            "unresolved": ["主用神不上卦，飞伏未实现前不补隐藏用神。"],
        }
    if len(useful_elements) > 1:
        _mark_unresolved(derived_lines, "主用神多现且五行不同，暂不强行合并原忌仇神。")
        return {
            "status": "ambiguous",
            "main_useful_god": main,
            "auxiliary_useful_gods": auxiliaries,
            "useful_god_elements": useful_elements,
            "role_elements": {},
            "by_line": [],
            "unresolved": ["主用神多现且五行不同，暂不强行合并原忌仇神。"],
        }

    useful_element = useful_elements[0]
    role_elements = _role_elements(useful_element)
    by_line = []
    for line in derived_lines:
        role = _line_role(line, main, role_elements)
        reason = _role_reason(line, main, useful_element, role)
        line["spirit_role"] = role
        line["spirit_role_reason"] = reason
        by_line.append(
            {
                "position": line["position"],
                "six_relative": line["six_relative"],
                "element": line["element"],
                "role": role,
                "role_name": ROLE_NAMES[role],
                "reason": reason,
                "moving": line["moving"],
                "effective_strength": line["effective_strength"],
                "void": line["void_state"]["is_void"],
            }
        )
    return {
        "status": "ready",
        "main_useful_god": main,
        "auxiliary_useful_gods": auxiliaries,
        "useful_god_elements": useful_elements,
        "role_elements": role_elements,
        "by_line": by_line,
        "unresolved": [],
    }


def build_completion_chain(
    derived_lines: list[dict],
    spirit_role_analysis: dict,
    useful_god_selection: dict,
    twelve_stage_analysis: dict | None = None,
    combination_factors: dict | None = None,
) -> dict:
    if spirit_role_analysis["status"] != "ready":
        return {
            "mode": "spirit_role_completion",
            "tendency": "insufficient",
            "supporting_factors": [],
            "blocking_factors": [],
            "mixed_factors": [],
            "unresolved": list(spirit_role_analysis["unresolved"]),
        }

    useful_lines = [line for line in derived_lines if line["spirit_role"] == "useful_god"]
    supporting = _supporting_factors(useful_lines, derived_lines)
    blocking = _blocking_factors(useful_lines, derived_lines)
    mixed = _mixed_factors(useful_god_selection, useful_lines)
    if twelve_stage_analysis:
        supporting.extend(twelve_stage_analysis["supporting_factors"])
        blocking.extend(twelve_stage_analysis["blocking_factors"])
        mixed.extend(twelve_stage_analysis["mixed_factors"])
    if combination_factors:
        supporting.extend(combination_factors["supporting_factors"])
        blocking.extend(combination_factors["blocking_factors"])
        mixed.extend(combination_factors["mixed_factors"])
    tendency = _tendency(supporting, blocking, mixed)
    return {
        "mode": "spirit_role_completion",
        "tendency": tendency,
        "supporting_factors": supporting,
        "blocking_factors": blocking,
        "mixed_factors": mixed,
        "unresolved": [
            "飞伏未实现，缺失用神不作隐藏补充。",
            "应期未实现，不输出具体日期。",
        ],
    }


def advanced_layers() -> dict:
    return {
        "enabled": ["spirit_roles", "twelve_stages", "three_combination"],
        "reserved": [
            "flying_hidden",
            "advance_retreat",
            "timing",
            "spirit_sha",
        ],
        "order": [
            "spirit_roles",
            "twelve_stages",
            "three_combination",
            "flying_hidden",
            "advance_retreat",
            "timing",
            "spirit_sha",
        ],
        "scope": "Only enabled layers may be used as evidence.",
    }


def _mark_unresolved(derived_lines: list[dict], reason: str) -> None:
    for line in derived_lines:
        line["spirit_role"] = "unresolved"
        line["spirit_role_reason"] = reason


def _role_elements(useful_element: str) -> dict:
    original = _element_generating(useful_element)
    avoiding = _element_controlling(useful_element)
    enemy = sorted({_element_controlling(original), _element_generating(avoiding)})
    neutral = sorted(set(GENERATING) - {useful_element, original, avoiding, *enemy})
    return {
        "useful_god": [useful_element],
        "original_spirit": [original],
        "avoiding_spirit": [avoiding],
        "enemy_spirit": enemy,
        "neutral_spirit": neutral,
    }


def _element_generating(target_element: str) -> str:
    return next(element for element, generated in GENERATING.items() if generated == target_element)


def _element_controlling(target_element: str) -> str:
    return next(element for element, controlled in CONTROLLING.items() if controlled == target_element)


def _line_role(line: dict, main_useful_god: str, role_elements: dict) -> str:
    if line["six_relative"] == main_useful_god:
        return "useful_god"
    element = line["element"]
    for role in ("original_spirit", "avoiding_spirit", "enemy_spirit"):
        if element in role_elements[role]:
            return role
    return "neutral_spirit"


def _role_reason(line: dict, main_useful_god: str, useful_element: str, role: str) -> str:
    if role == "useful_god":
        return f"本爻六亲为主用神{main_useful_god}。"
    if role == "original_spirit":
        return f"本爻{line['element']}生主用神{useful_element}，为原神。"
    if role == "avoiding_spirit":
        return f"本爻{line['element']}克主用神{useful_element}，为忌神。"
    if role == "enemy_spirit":
        return f"本爻{line['element']}克原神或生忌神，为仇神。"
    return "本爻不直接生克主用神链，为闲神。"


def _supporting_factors(useful_lines: list[dict], derived_lines: list[dict]) -> list[dict]:
    factors = []
    for line in useful_lines:
        factors.append({"type": "useful_god_present", "line": line["position"], "summary": f"主用神{line['six_relative']}上卦。"})
        if line["effective_strength"] in {"strong", "very_strong"}:
            factors.append({"type": "useful_god_has_strength", "line": line["position"], "summary": f"主用神为{line['effective_strength']}。"})
        if not line["void_state"]["is_void"]:
            factors.append({"type": "useful_god_not_void", "line": line["position"], "summary": "主用神不空。"})
    for line in derived_lines:
        if line["spirit_role"] == "original_spirit" and line["effective_strength"] in {"strong", "very_strong"}:
            factors.append({"type": "original_spirit_present_with_strength", "line": line["position"], "summary": "原神上卦且有力。"})
    return factors


def _blocking_factors(useful_lines: list[dict], derived_lines: list[dict]) -> list[dict]:
    factors = []
    for useful in useful_lines:
        if useful["void_state"]["is_void"]:
            factors.append({"type": "useful_god_void", "line": useful["position"], "summary": "主用神旬空。"})
        if useful["effective_strength"] in {"weak", "very_weak"}:
            factors.append({"type": "useful_god_weak", "line": useful["position"], "summary": f"主用神为{useful['effective_strength']}。"})
        if useful["month_state"]["branch_relation"] == "clash":
            factors.append({"type": "useful_god_month_clash", "line": useful["position"], "summary": "主用神逢月冲。"})
        if useful["day_state"]["branch_relation"] == "clash":
            factors.append({"type": "useful_god_day_clash", "line": useful["position"], "summary": "主用神逢日冲。"})
    for line in derived_lines:
        if line["spirit_role"] == "avoiding_spirit" and line["effective_strength"] in {"strong", "very_strong"}:
            factors.append({"type": "avoiding_spirit_present_with_strength", "line": line["position"], "summary": "忌神上卦且有力。"})
        if line["moving"]:
            for useful in useful_lines:
                relation = element_relation(line["element"], useful["element"])
                if line["spirit_role"] == "avoiding_spirit" and relation == "controls":
                    factors.append(
                        {
                            "type": "avoiding_spirit_moving_controls_useful_god",
                            "line": line["position"],
                            "target_line": useful["position"],
                            "summary": f"忌神{line['six_relative']}{line['element']}发动克主用神{useful['six_relative']}{useful['element']}。",
                        }
                    )
                elif relation == "controls":
                    factors.append(
                        {
                            "type": "moving_line_controls_useful_god",
                            "line": line["position"],
                            "target_line": useful["position"],
                            "summary": f"动爻{line['element']}克主用神{useful['element']}。",
                        }
                    )
    return factors


def _mixed_factors(useful_god_selection: dict, useful_lines: list[dict]) -> list[dict]:
    factors = []
    result = useful_god_selection["selection_result"]
    if result["status"] == "layered":
        factors.append(
            {
                "type": "layered_auxiliary",
                "summary": f"{'、'.join(result['auxiliary_useful_gods'])}为辅助轴，需与{result['main_useful_god']}主轴分层。",
            }
        )
    for line in useful_lines:
        if line["void_state"]["is_void"] and line["effective_strength"] in {"strong", "very_strong"}:
            factors.append({"type": "strong_but_void", "line": line["position"], "summary": "主用神有力但旬空。"})
    return factors


def _tendency(supporting: list[dict], blocking: list[dict], mixed: list[dict]) -> str:
    strong_blocking = [item for item in blocking if item["type"] in {"avoiding_spirit_moving_controls_useful_god", "useful_god_void", "useful_god_month_clash"}]
    if strong_blocking and supporting:
        return "mixed"
    if strong_blocking:
        return "blocked"
    if blocking and supporting:
        return "mixed"
    if supporting and not mixed:
        return "supported"
    if supporting:
        return "mixed"
    return "insufficient"
