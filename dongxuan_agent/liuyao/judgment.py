from __future__ import annotations

from .combinations import build_combination_analysis, completion_factors
from .flying_hidden import (
    attach_hidden_spirits,
    build_flying_hidden_analysis,
    completion_factors as flying_hidden_completion_factors,
)
from .imagery import build_imagery_context, build_useful_god_selection
from .relations import branch_relation, element_relation, return_relation_label
from .six_spirits import assign_six_spirits
from .spirit_roles import advanced_layers, build_completion_chain, build_spirit_role_analysis
from .strength import BRANCH_ELEMENTS, effective_strength, extreme_state, seasonal_state
from .templates import build_question_template
from .twelve_stages import attach_twelve_stages, build_twelve_stage_analysis


def enrich_payload(payload: dict) -> dict:
    derived_lines = build_derived_lines(payload)
    question_template = build_question_template(payload["question_context"]["domain"], payload["input"]["question"])
    useful_gods = build_useful_god_analysis(payload, derived_lines)
    imagery_context = build_imagery_context(payload["input"]["question"], useful_gods["domain"])
    useful_god_selection = build_useful_god_selection(payload, derived_lines, useful_gods, imagery_context, question_template)
    spirit_role_analysis = build_spirit_role_analysis(derived_lines, useful_god_selection)
    attach_twelve_stages(derived_lines)
    twelve_stage_analysis = build_twelve_stage_analysis(derived_lines)
    combination_analysis = build_combination_analysis(derived_lines, spirit_role_analysis, payload["calendar"])
    attach_hidden_spirits(derived_lines, payload["najia"]["hidden_spirits"])
    flying_hidden_analysis = build_flying_hidden_analysis(payload["najia"]["hidden_spirits"], spirit_role_analysis)
    completion_chain = build_completion_chain(
        derived_lines,
        spirit_role_analysis,
        useful_god_selection,
        twelve_stage_analysis,
        completion_factors(combination_analysis),
        flying_hidden_completion_factors(flying_hidden_analysis),
    )
    six_spirits = assign_six_spirits(payload["calendar"]["day_gz"], derived_lines)
    _attach_six_spirits_to_lines(derived_lines, six_spirits)
    relations = build_relations(payload, derived_lines, useful_gods)
    payload["derived_lines"] = derived_lines
    payload["question_template"] = question_template
    payload["useful_god_analysis"] = useful_gods
    payload["imagery_context"] = imagery_context
    payload["useful_god_selection"] = useful_god_selection
    payload["spirit_role_analysis"] = spirit_role_analysis
    payload["twelve_stage_analysis"] = twelve_stage_analysis
    payload["combination_analysis"] = combination_analysis
    payload["flying_hidden_analysis"] = flying_hidden_analysis
    payload["completion_chain"] = completion_chain
    payload["advanced_layers"] = advanced_layers()
    payload["six_spirits"] = six_spirits
    payload["auxiliary_marks"] = auxiliary_marks()
    payload["relations"] = relations
    payload["judgment_frame"] = judgment_frame(bool(payload["hexagram"]["moving_lines"]))
    payload["prompt_contract"] = prompt_contract()
    return payload


def build_derived_lines(payload: dict) -> list[dict]:
    candidates = _candidate_roles(payload["question_context"])
    month_branch = payload["calendar"]["month_branch"]
    day_branch = payload["calendar"]["day_branch"]
    month_element = BRANCH_ELEMENTS[month_branch]
    day_element = BRANCH_ELEMENTS[day_branch]
    xunkong = payload["calendar"]["xunkong"]
    najia_by_position = {line["position"]: line for line in payload["najia"]["lines"]}
    lines = []
    for line in payload["lines"]:
        najia = najia_by_position[line["position"]]
        support, weakening = _strength_factors(najia, line, month_branch, day_branch, xunkong)
        seasonal = seasonal_state(najia["element"], month_branch)
        candidate_roles = candidates.get(najia["six_relative"], [])
        month = {
            "month_branch": month_branch,
            "month_element": month_element,
            "seasonal_state": seasonal,
            "branch_relation": branch_relation(month_branch, najia["branch"]),
            "element_relation": _named_element_relation("month", month_element, "line", najia["element"]),
            "evidence": _month_evidence(najia, month_branch, month_element, seasonal),
        }
        day = {
            "day_branch": day_branch,
            "day_element": day_element,
            "branch_relation": branch_relation(day_branch, najia["branch"]),
            "element_relation": _named_element_relation("day", day_element, "line", najia["element"]),
            "evidence": _day_evidence(najia, day_branch, day_element),
        }
        lines.append(
            {
                **line,
                "stem_branch": najia["stem_branch"],
                "branch": najia["branch"],
                "element": najia["element"],
                "six_relative": najia["six_relative"],
                "role": najia["role"],
                "is_shi": najia["role"] == "世",
                "is_ying": najia["role"] == "应",
                "is_candidate_useful_god": bool(candidate_roles),
                "candidate_useful_god_roles": candidate_roles,
                "month_state": month,
                "day_state": day,
                "void_state": {
                    "xunkong": xunkong,
                    "is_void": najia["branch"] in xunkong,
                },
                "changed_line_state": None,
                "effective_strength": effective_strength(seasonal, support, weakening),
                "extreme_state": extreme_state(seasonal, support, weakening),
                "strength_evidence": _strength_evidence(seasonal, support, weakening),
                "judgment_caution": _judgment_caution(candidate_roles, weakening),
            }
        )
    return lines


def build_useful_god_analysis(payload: dict, derived_lines: list[dict]) -> dict:
    candidates = []
    missing = []
    for index, item in enumerate(payload["question_context"]["candidate_useful_gods"]):
        relative = item["six_relative"]
        if relative == "世应":
            continue
        matches = [
            _matching_line(line)
            for line in derived_lines
            if line["six_relative"] == relative
        ]
        if not matches:
            missing.append(relative)
        candidates.append(
            {
                "six_relative": relative,
                "priority": "primary" if index == 0 else "secondary",
                "reason": item["reason"],
                "matching_lines": matches,
                "selection_constraints": [
                    "候选用神不等于最终用神",
                    "必须检查世应关系",
                    "必须检查月令、日辰、动爻、变爻对候选用神的作用",
                ],
            }
        )
    return {
        "domain": payload["question_context"]["domain"],
        "candidates": candidates,
        "missing_candidates": missing,
        "unresolved": [
            "MVP 只定位候选用神，不自动定最终用神",
        ],
    }


def build_relations(payload: dict, derived_lines: list[dict], useful_gods: dict) -> dict:
    shi = _line_by_role(derived_lines, "世")
    ying = _line_by_role(derived_lines, "应")
    return {
        "month_day": _month_day_relations(payload, derived_lines),
        "shi_ying": _shi_ying_relation(shi, ying),
        "moving_effects": _moving_effects(payload, derived_lines, useful_gods),
    }


def judgment_frame(has_moving_lines: bool) -> dict:
    return {
        "mode": "minimal_loop",
        "static_chart": not has_moving_lines,
        "steps": [
            {"step": 1, "name": "question_domain", "instruction": "确认所问事项和候选用神，不得跳过问题语境。"},
            {"step": 2, "name": "locate_useful_gods", "instruction": "把候选用神落到具体爻位，记录缺失或多现。"},
            {"step": 3, "name": "check_shi_ying", "instruction": "检查世应六亲、五行、月日状态和彼此生克冲合。"},
            {"step": 4, "name": "check_month_day_strength", "instruction": "先看月令旺相休囚死，再看日辰生克冲合与旬空。"},
            {"step": 5, "name": "check_moving_changed_lines", "instruction": "检查动爻对世应和候选用神的作用，再看回头生克。"},
            {"step": 6, "name": "synthesize", "instruction": "只输出倾向、证据和不确定项，不编造未实现规则。"},
        ],
        "stop_conditions": [
            "关键字段缺失时，不得继续自由推断",
            "候选用神缺失且伏神未实现时，只能标记为未决",
        ],
    }


def prompt_contract() -> dict:
    return {
        "must_use_fields": [
            "derived_lines",
            "useful_god_analysis",
            "useful_god_selection",
            "spirit_role_analysis",
            "twelve_stage_analysis",
            "combination_analysis",
            "completion_chain",
            "advanced_layers",
            "question_template",
            "six_spirits",
            "relations",
            "judgment_frame",
        ],
        "must_not_infer": [
            "未实现的飞伏",
            "未实现的三合局",
            "未实现的应期",
            "未实现的神煞命中",
            "八字旺衰或格局",
            "大六壬四课三传",
        ],
        "output_sections": [
            "卦体摘要",
            "用神定位",
            "世应关系",
            "旺衰与月日",
            "动变作用",
            "综合倾向",
            "不确定项",
        ],
    }


def _attach_six_spirits_to_lines(derived_lines: list[dict], six_spirits: dict) -> None:
    by_position = {line["position"]: line for line in six_spirits["lines"]}
    for line in derived_lines:
        spirit = by_position[line["position"]]
        line["six_spirit"] = {
            "spirit": spirit["spirit"],
            "imagery": spirit["imagery"],
            "cautions": spirit["cautions"],
        }


def auxiliary_marks() -> dict:
    return {
        "enabled": [],
        "reserved": ["驿马", "桃花", "贵人"],
        "scope": "预留字段；当前不计算神煞，不得在 prompt 中编造命中。",
    }


def _candidate_roles(question_context: dict) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for index, item in enumerate(question_context["candidate_useful_gods"]):
        relative = item["six_relative"]
        if relative == "世应":
            continue
        result.setdefault(relative, []).append("主候选" if index == 0 else "辅助候选")
    return result


def _strength_factors(najia: dict, line: dict, month_branch: str, day_branch: str, xunkong: list[str]) -> tuple[list[str], list[str]]:
    support: list[str] = []
    weakening: list[str] = []
    for label, branch in (("月支", month_branch), ("日支", day_branch)):
        branch_element = BRANCH_ELEMENTS[branch]
        rel = element_relation(branch_element, najia["element"])
        br_rel = branch_relation(branch, najia["branch"])
        if rel in {"generates", "same"}:
            support.append(f"{label}生扶")
        if rel == "controls":
            weakening.append(f"{label}克制")
        if br_rel == "same":
            support.append(f"{label}同支")
        if br_rel == "clash":
            weakening.append(f"{label}冲")
    if line["moving"]:
        support.append("动爻发动")
    if najia["branch"] in xunkong:
        weakening.append("旬空")
    return support, weakening


def _month_evidence(najia: dict, month_branch: str, month_element: str, seasonal: str) -> list[str]:
    return [
        f"{month_branch}月{month_element}当令",
        f"{najia['element']}在月令为{seasonal}",
        _branch_relation_text(month_branch, najia["branch"]),
    ]


def _day_evidence(najia: dict, day_branch: str, day_element: str) -> list[str]:
    return [
        f"日辰{day_branch}属{day_element}",
        _branch_relation_text(day_branch, najia["branch"]),
        _element_relation_text("日辰", day_element, "本爻", najia["element"]),
    ]


def _branch_relation_text(left: str, right: str) -> str:
    rel = branch_relation(left, right)
    names = {"same": "同支", "clash": "冲", "combine": "合", "none": "无直接冲合"}
    return f"{left}{right}{names[rel]}"


def _element_relation_text(actor_name: str, actor_element: str, target_name: str, target_element: str) -> str:
    rel = element_relation(actor_element, target_element)
    names = {
        "same": "同类",
        "generates": "生",
        "controls": "克",
        "generated_by": "被生",
        "controlled_by": "被克",
        "none": "无直接作用",
    }
    return f"{actor_name}{actor_element}{names[rel]}{target_name}{target_element}"


def _named_element_relation(actor_name: str, actor_element: str, target_name: str, target_element: str) -> str:
    rel = element_relation(actor_element, target_element)
    if rel == "same":
        return "same"
    if rel == "generates":
        return f"{actor_name}_generates_{target_name}"
    if rel == "controls":
        return f"{actor_name}_controls_{target_name}"
    if rel == "generated_by":
        return f"{target_name}_generates_{actor_name}"
    if rel == "controlled_by":
        return f"{target_name}_controls_{actor_name}"
    return "none"


def _strength_evidence(seasonal: str, support: list[str], weakening: list[str]) -> list[str]:
    evidence = [f"月令为{seasonal}"]
    evidence.extend(support)
    evidence.extend(weakening)
    return evidence


def _judgment_caution(candidate_roles: list[str], weakening: list[str]) -> list[str]:
    caution = ["旺衰不直接等于吉凶，仍需合看用神、世应、动变。"]
    if candidate_roles and weakening:
        caution.append("候选用神见削弱因素时不能直接作吉论。")
    return caution


def _matching_line(line: dict) -> dict:
    return {
        "position": line["position"],
        "name": line["name"],
        "role": line["role"],
        "element": line["element"],
        "branch": line["branch"],
        "moving": line["moving"],
        "effective_strength": line["effective_strength"],
        "extreme_state": line["extreme_state"],
    }


def _month_day_relations(payload: dict, derived_lines: list[dict]) -> dict:
    return {
        "month_branch": payload["calendar"]["month_branch"],
        "month_element": BRANCH_ELEMENTS[payload["calendar"]["month_branch"]],
        "day_branch": payload["calendar"]["day_branch"],
        "day_element": BRANCH_ELEMENTS[payload["calendar"]["day_branch"]],
        "by_line": [
            {
                "position": line["position"],
                "month": {
                    "branch_relation": line["month_state"]["branch_relation"],
                    "element_relation": line["month_state"]["element_relation"],
                    "seasonal_state": line["month_state"]["seasonal_state"],
                },
                "day": {
                    "branch_relation": line["day_state"]["branch_relation"],
                    "element_relation": line["day_state"]["element_relation"],
                },
            }
            for line in derived_lines
        ],
    }


def _shi_ying_relation(shi: dict, ying: dict) -> dict:
    rel = _named_element_relation("shi", shi["element"], "ying", ying["element"])
    return {
        "shi_position": shi["position"],
        "ying_position": ying["position"],
        "branch_relation": branch_relation(shi["branch"], ying["branch"]),
        "element_relation": rel,
        "summary": _relation_summary("世爻", shi["element"], "应爻", ying["element"]),
    }


def _moving_effects(payload: dict, derived_lines: list[dict], useful_gods: dict) -> list[dict]:
    moving_positions = set(payload["hexagram"]["moving_lines"])
    if not moving_positions:
        return []
    targets = _moving_targets(derived_lines, useful_gods)
    effects = []
    for line in derived_lines:
        if line["position"] not in moving_positions:
            continue
        effects.append(
            {
                "actor_position": line["position"],
                "actor_branch": line["branch"],
                "actor_element": line["element"],
                "targets": [_target_relation(line, target) for target in targets],
                "changed_line": _changed_line_relation(payload, line),
            }
        )
    return effects


def _moving_targets(derived_lines: list[dict], useful_gods: dict) -> list[dict]:
    targets = []
    for target_name, role in (("shi", "世"), ("ying", "应")):
        line = _line_by_role(derived_lines, role)
        targets.append({"target": target_name, **line})
    seen = {(item["target"], item["position"]) for item in targets}
    for candidate in useful_gods["candidates"]:
        for match in candidate["matching_lines"]:
            key = ("candidate_useful_god", match["position"])
            if key in seen:
                continue
            line = derived_lines[match["position"] - 1]
            targets.append({"target": "candidate_useful_god", **line})
            seen.add(key)
    return targets


def _target_relation(actor: dict, target: dict) -> dict:
    return {
        "target": target["target"],
        "target_position": target["position"],
        "element_relation": _named_element_relation("actor", actor["element"], "target", target["element"]),
        "branch_relation": branch_relation(actor["branch"], target["branch"]),
    }


def _changed_line_relation(payload: dict, actor: dict) -> dict:
    changed_bit = payload["hexagram"]["changed"]["binary_bottom_to_top"][actor["position"] - 1]
    changed_branch = _changed_branch(actor["branch"], changed_bit)
    changed_element = BRANCH_ELEMENTS[changed_branch]
    return {
        "changed_branch": changed_branch,
        "changed_element": changed_element,
        "return_relation": _named_element_relation("changed", changed_element, "actor", actor["element"]),
        "return_label": return_relation_label(actor["element"], changed_element),
    }


def _changed_branch(original_branch: str, changed_bit: str) -> str:
    # MVP keeps changed-line branch explicit and deterministic without full changed-hexagram najia remapping.
    # Yang changes use the next branch, yin changes use the previous branch in the terrestrial sequence.
    branches = list(BRANCH_ELEMENTS)
    index = branches.index(original_branch)
    offset = 1 if changed_bit == "1" else -1
    return branches[(index + offset) % len(branches)]


def _line_by_role(derived_lines: list[dict], role: str) -> dict:
    for line in derived_lines:
        if line["role"] == role:
            return line
    raise RuntimeError(f"缺少{role}爻")


def _relation_summary(left_name: str, left_element: str, right_name: str, right_element: str) -> str:
    rel = element_relation(left_element, right_element)
    labels = {
        "same": "比和",
        "generates": "生",
        "controls": "克",
        "generated_by": "受生于",
        "controlled_by": "受克于",
        "none": "无直接作用",
    }
    return f"{left_name}{labels[rel]}{right_name}"
