from __future__ import annotations


SUPPORT_ELEMENTS = {
    "木": ("水", "木"),
    "火": ("木", "火"),
    "土": ("火", "土"),
    "金": ("土", "金"),
    "水": ("金", "水"),
}

DRAIN_ELEMENTS = {
    "木": ("火", "土", "金"),
    "火": ("土", "金", "水"),
    "土": ("金", "水", "木"),
    "金": ("水", "木", "火"),
    "水": ("木", "火", "土"),
}


def analyze_remedy(strength_analysis: dict, climate_analysis: dict, pattern_analysis: dict) -> dict:
    problems = []
    candidates = []
    conflicts = []

    _add_climate_remedy(climate_analysis, problems, candidates)
    _add_strength_remedy(strength_analysis, problems, candidates)
    _add_pattern_remedy(pattern_analysis, problems, candidates, conflicts)
    _add_root_conflicts(strength_analysis, candidates, conflicts)

    priority = _priority(problems)
    usable = _dedupe(candidate["element"] for candidate in candidates)
    avoid = _avoid_gods(climate_analysis, strength_analysis)
    return {
        "problems": problems,
        "remedy_candidates": candidates,
        "conflicts": conflicts,
        "priority": priority,
        "usable_gods": usable,
        "avoid_gods": avoid,
        "status": "候选病药，不作最终用神定论",
        "uncertainty": [
            "病药 V1 只综合调候、扶抑、格局扰动三类证据，不等同最终用神。",
            "调候药、扶抑药、格局药冲突时，V1 只列冲突和优先级，不强行裁断。",
        ],
    }


def _add_climate_remedy(climate: dict, problems: list[dict], candidates: list[dict]) -> None:
    temperature = climate["temperature"]
    moisture = climate["moisture"]
    if temperature == "偏寒" or moisture == "偏湿":
        problems.append({
            "type": "调候病",
            "description": f"{climate['season_profile']}，局见{temperature}{moisture}，寒湿为病。",
            "evidence": climate["evidence"],
        })
        for element in climate["preferred_elements"]:
            candidates.append({
                "element": element,
                "role": "调候药",
                "strength": "强",
                "evidence": [f"climate_analysis.preferred_elements 包含 {element}"],
            })
    elif temperature == "偏热" or moisture == "偏燥":
        problems.append({
            "type": "调候病",
            "description": f"{climate['season_profile']}，局见{temperature}{moisture}，燥热为病。",
            "evidence": climate["evidence"],
        })
        for element in climate["preferred_elements"]:
            candidates.append({
                "element": element,
                "role": "调候药",
                "strength": "强",
                "evidence": [f"climate_analysis.preferred_elements 包含 {element}"],
            })


def _add_strength_remedy(strength: dict, problems: list[dict], candidates: list[dict]) -> None:
    day = strength["day_master_strength"]
    level = day["level"]
    day_element = day["day_element"]
    if level in {"偏弱", "中和偏弱"}:
        problems.append({
            "type": "扶抑病",
            "description": f"日主{day['day_master']}为{level}，扶身不足为病。",
            "evidence": day["evidence"],
        })
        for element in SUPPORT_ELEMENTS[day_element]:
            candidates.append({"element": element, "role": "扶抑药", "strength": "中", "evidence": [f"{element}可生扶日主{day_element}"]})
    elif level in {"偏旺", "中和偏旺"}:
        problems.append({
            "type": "扶抑病",
            "description": f"日主{day['day_master']}为{level}，宜泄耗制过旺。",
            "evidence": day["evidence"],
        })
        for element in DRAIN_ELEMENTS[day_element]:
            candidates.append({"element": element, "role": "扶抑药", "strength": "中", "evidence": [f"{element}可泄耗制日主{day_element}"]})


def _add_pattern_remedy(pattern: dict, problems: list[dict], candidates: list[dict], conflicts: list[str]) -> None:
    primary = pattern["primary_pattern"]
    for item in pattern.get("damage_evidence", []):
        if "未见明确" in item:
            continue
        problems.append({
            "type": "格局病",
            "description": item,
            "evidence": pattern.get("formation_evidence", []) + [item],
        })
        conflicts.append(item)
    name = primary["name"]
    if name in {"食神格", "伤官格"}:
        candidates.append({"element": "财", "role": "格局药", "strength": "弱", "evidence": [f"{name}可取财星流通食伤之气，但需另辨全局。"]})
    elif name in {"正官格", "七杀格"}:
        candidates.append({"element": "印", "role": "格局药", "strength": "弱", "evidence": [f"{name}可取印星化杀护官，但 V1 不定成败。"]})
    elif name in {"正财格", "偏财格"}:
        candidates.append({"element": "官", "role": "格局药", "strength": "弱", "evidence": [f"{name}可取官星护财成事，但 V1 不定成败。"]})


def _add_root_conflicts(strength: dict, candidates: list[dict], conflicts: list[str]) -> None:
    forces = strength["element_forces"]
    for candidate in candidates:
        element = candidate["element"]
        if element not in forces:
            continue
        notes = forces[element].get("damage_notes") or []
        if notes:
            conflicts.append(f"{element}虽为{candidate['role']}，但根气/支位受{'、'.join(notes)}影响。")
    fire_notes = forces.get("火", {}).get("damage_notes") or []
    if fire_notes:
        conflicts.append("午火虽可暖局，但受" + "、".join(fire_notes) + "，药力不纯。")


def _priority(problems: list[dict]) -> str:
    if any(problem["type"] == "调候病" for problem in problems):
        return "调候优先"
    if any(problem["type"] == "扶抑病" for problem in problems):
        return "扶抑优先"
    if any(problem["type"] == "格局病" for problem in problems):
        return "格局优先"
    return "暂不定优先"


def _avoid_gods(climate: dict, strength: dict) -> list[str]:
    avoid = []
    if climate["temperature"] == "偏寒" or climate["moisture"] == "偏湿":
        avoid.append("水")
    if climate["temperature"] == "偏热" or climate["moisture"] == "偏燥":
        avoid.extend(["火", "燥土"])
    day = strength["day_master_strength"]
    if day["level"] in {"偏弱", "中和偏弱"}:
        avoid.extend(DRAIN_ELEMENTS[day["day_element"]])
    elif day["level"] in {"偏旺", "中和偏旺"}:
        avoid.extend(SUPPORT_ELEMENTS[day["day_element"]])
    return _dedupe(avoid)


def _dedupe(values) -> list:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
