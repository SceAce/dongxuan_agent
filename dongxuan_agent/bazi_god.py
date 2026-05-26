from __future__ import annotations


ROLE_SCORE = {
    "调候药": 4,
    "扶抑药": 3,
    "格局药": 2,
}

STRENGTH_SCORE = {
    "强": 2,
    "中": 1,
    "弱": 0,
}


def build_god_candidates(remedy_analysis: dict, strength_analysis: dict, climate_analysis: dict, pattern_analysis: dict) -> dict:
    grouped: dict[str, dict] = {}
    for candidate in remedy_analysis["remedy_candidates"]:
        element = candidate["element"]
        item = grouped.setdefault(
            element,
            {
                "element": element,
                "score": 0,
                "roles": [],
                "supporting_evidence": [],
                "conflicting_evidence": [],
            },
        )
        item["score"] += ROLE_SCORE.get(candidate["role"], 1) + STRENGTH_SCORE.get(candidate["strength"], 0)
        if candidate["role"] == "调候药" and element == "火":
            item["score"] += 3
        if candidate["role"] not in item["roles"]:
            item["roles"].append(candidate["role"])
        item["supporting_evidence"].extend(candidate.get("evidence", []))

    for conflict in remedy_analysis.get("conflicts", []):
        for element, item in grouped.items():
            if element in conflict:
                item["conflicting_evidence"].append(conflict)
                item["score"] -= 1

    candidates = sorted(grouped.values(), key=lambda item: (item["score"], _element_priority(item["element"])), reverse=True)
    return {
        "candidate_gods": candidates,
        "supporting_evidence": _supporting_evidence(remedy_analysis, climate_analysis, pattern_analysis),
        "conflicting_evidence": remedy_analysis.get("conflicts", []),
        "priority": remedy_analysis["priority"],
        "avoid_gods": remedy_analysis["avoid_gods"],
        "status": "候选用神，不作最终定论",
        "uncertainty": [
            "用神候选 V1 只对调候药、扶抑药、格局药做证据汇总和排序，不输出最终用神。",
            "候选五行与十神尚未完全映射为可执行断语，需结合具体问题和岁运触发。",
        ],
    }


def _supporting_evidence(remedy: dict, climate: dict, pattern: dict) -> list[str]:
    evidence = [
        f"病药优先级：{remedy['priority']}。",
        f"调候：{climate['season_profile']}，候选 {'、'.join(climate['preferred_elements']) or '无明显调候药'}。",
        f"格局：{pattern['primary_pattern']['name']}，状态 {pattern['status']}。",
    ]
    for candidate in remedy["remedy_candidates"]:
        evidence.append(f"{candidate['element']}作为{candidate['role']}：{'、'.join(candidate.get('evidence', []))}")
    return evidence


def _element_priority(element: str) -> int:
    return {
        "火": 5,
        "燥土": 4,
        "土": 3,
        "金": 2,
        "水": 1,
        "木": 1,
    }.get(element, 0)
