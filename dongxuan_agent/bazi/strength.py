from __future__ import annotations

from .chart import BRANCH_COMBINE, BRANCH_HARM, HIDDEN_STEMS, BaziChart
from ..constants import (
    BRANCH_ELEMENTS,
    BRANCH_OPPOSITE,
    BRANCH_PUNISH,
    CONTROLLING,
    GENERATING,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
)


ELEMENTS = ("木", "火", "土", "金", "水")

HIDDEN_WEIGHTS = (1.0, 0.55, 0.3)

SEASON_POWER = {
    "寅": {"木": 1.25, "火": 0.85, "土": 0.75, "金": 0.55, "水": 0.7},
    "卯": {"木": 1.35, "火": 0.8, "土": 0.65, "金": 0.5, "水": 0.65},
    "辰": {"木": 0.8, "火": 0.7, "土": 1.1, "金": 0.75, "水": 0.9},
    "巳": {"木": 0.75, "火": 1.25, "土": 1.0, "金": 0.7, "水": 0.45},
    "午": {"木": 0.65, "火": 1.35, "土": 1.05, "金": 0.55, "水": 0.4},
    "未": {"木": 0.65, "火": 1.0, "土": 1.2, "金": 0.65, "水": 0.45},
    "申": {"木": 0.45, "火": 0.55, "土": 0.85, "金": 1.25, "水": 0.9},
    "酉": {"木": 0.4, "火": 0.5, "土": 0.75, "金": 1.35, "水": 0.8},
    "戌": {"木": 0.45, "火": 0.75, "土": 1.2, "金": 1.0, "水": 0.5},
    "亥": {"木": 0.85, "火": 0.45, "土": 0.55, "金": 0.75, "水": 1.25},
    "子": {"木": 0.65, "火": 0.4, "土": 0.55, "金": 0.8, "水": 1.35},
    "丑": {"木": 0.45, "火": 0.45, "土": 1.15, "金": 0.95, "水": 1.0},
}


def analyze_strength(chart: BaziChart) -> dict:
    payload = chart.to_dict()
    pillars = payload["pillars"]
    month_branch = _pillar(pillars, "月柱")["branch"]
    day_master = payload["day_master"]
    day_element = STEM_ELEMENTS[day_master]
    branch_relations = payload.get("branch_relationships") or []
    forces = {
        element: {
            "count": 0,
            "season_power": SEASON_POWER[month_branch][element],
            "stem_power": 0.0,
            "root_power": 0.0,
            "effective_power": 0.0,
            "root_status": "无根",
            "roots": [],
            "damage_notes": [],
        }
        for element in ELEMENTS
    }

    for pillar in pillars:
        stem_element = STEM_ELEMENTS[pillar["stem"]]
        forces[stem_element]["count"] += 1
        forces[stem_element]["stem_power"] += 1.0 if pillar["name"] in {"月柱", "日柱"} else 0.85

        for index, hidden in enumerate(HIDDEN_STEMS[pillar["branch"]]):
            element = STEM_ELEMENTS[hidden]
            weight = HIDDEN_WEIGHTS[index]
            if pillar["name"] == "月柱":
                weight *= 1.35
            if pillar["name"] == "日柱":
                weight *= 1.15
            damage = _root_damage(pillar["branch"], branch_relations)
            if damage:
                weight *= 0.7
            quality = _root_quality(hidden, pillar["branch"], index, damage)
            root = {
                "branch": pillar["branch"],
                "pillar": pillar["name"],
                "stem": hidden,
                "element": element,
                "layer": ("本气", "中气", "余气")[index],
                "quality": quality,
                "base_weight": HIDDEN_WEIGHTS[index],
                "effective_weight": round(weight, 3),
                "damaged": bool(damage),
                "damage": damage,
            }
            forces[element]["count"] += 1
            forces[element]["root_power"] += weight
            forces[element]["roots"].append(root)
            for note in damage:
                if note not in forces[element]["damage_notes"]:
                    forces[element]["damage_notes"].append(note)

    for element, item in forces.items():
        item["stem_power"] = round(item["stem_power"], 3)
        item["root_power"] = round(item["root_power"], 3)
        item["effective_power"] = round((item["stem_power"] + item["root_power"]) * item["season_power"], 3)
        item["root_status"] = _root_status(item["roots"])
        item["season_power"] = round(item["season_power"], 3)

    support_power = forces[day_element]["effective_power"] + forces[_generates(day_element)]["effective_power"]
    drain_elements = {
        GENERATING[day_element],
        CONTROLLING[day_element],
        _controls(day_element),
    }
    drain_power = sum(forces[element]["effective_power"] for element in drain_elements)
    score = round(support_power - drain_power, 3)
    day_strength = {
        "day_master": day_master,
        "day_element": day_element,
        "level": _strength_level(score),
        "score": score,
        "support_power": round(support_power, 3),
        "drain_power": round(drain_power, 3),
        "root_summary": _root_summary(day_element, forces[day_element]),
        "evidence": _strength_evidence(day_master, day_element, month_branch, forces, score),
        "uncertainty": [
            "旺衰 V1 为可解释评分模型，先处理月令、透干、根气和原局冲合刑害提示；未处理复杂合化成败、会局成局、从格。",
            "根受损 V1 只做降权和提示，不直接判定根气完全消失。",
        ],
    }

    return {
        "month_branch": month_branch,
        "day_master_strength": day_strength,
        "element_forces": forces,
    }


def _pillar(pillars: list[dict], name: str) -> dict:
    return next(item for item in pillars if item["name"] == name)


def _root_quality(stem: str, branch: str, index: int, damage: list[str]) -> str:
    if damage:
        return "根受损"
    if STEM_LODGING_BRANCH.get(stem) == branch:
        return "真根"
    return ("真根", "偏根", "余根")[index]


def _root_damage(branch: str, relations: list[dict]) -> list[str]:
    notes = []
    for relation in relations:
        branches = relation["branches"]
        if branch not in branches:
            continue
        relation_type = relation["type"]
        if relation_type in {"冲", "刑", "自刑", "害"}:
            notes.append(f"{branches}{relation_type}")
        elif relation_type == "合":
            element = relation.get("element")
            own_element = BRANCH_ELEMENTS[branch]
            if element and element != own_element:
                notes.append(f"{branches}合{element}")
    return notes


def _root_status(roots: list[dict]) -> str:
    if not roots:
        return "无根"
    if any(root["quality"] == "真根" for root in roots):
        return "有真根"
    if any(root["quality"] == "根受损" for root in roots):
        return "根受损"
    if any(root["quality"] == "偏根" for root in roots):
        return "有偏根"
    return "虚根"


def _generates(element: str) -> str:
    return next(source for source, target in GENERATING.items() if target == element)


def _controls(element: str) -> str:
    return next(source for source, target in CONTROLLING.items() if target == element)


def _strength_level(score: float) -> str:
    if score >= 3.0:
        return "偏旺"
    if score >= 1.0:
        return "中和偏旺"
    if score > -1.0:
        return "中和"
    if score > -3.0:
        return "中和偏弱"
    return "偏弱"


def _root_summary(day_element: str, force: dict) -> str:
    if not force["roots"]:
        return f"{day_element}无地支根气。"
    parts = [
        f"{root['branch']}中{root['stem']}为{root['quality']}"
        for root in force["roots"]
    ]
    return f"{day_element}根气：" + "，".join(parts) + "。"


def _strength_evidence(day_master: str, day_element: str, month_branch: str, forces: dict, score: float) -> list[str]:
    evidence = [
        f"{day_master}{day_element}生于{month_branch}月，季节力量系数 {forces[day_element]['season_power']}。",
    ]
    if forces[day_element]["season_power"] < 1:
        evidence.append(f"{month_branch}月不得令。")
        evidence.append(f"{month_branch}月不得令，故不可只凭根气断旺。")
    elif forces[day_element]["season_power"] > 1:
        evidence.append(f"{month_branch}月得令。")
    evidence.append(f"同类有效力 {forces[day_element]['effective_power']}，印星有效力 {forces[_generates(day_element)]['effective_power']}。")
    evidence.append(f"克泄耗合计后评分 {round(score, 3)}。")
    return evidence
