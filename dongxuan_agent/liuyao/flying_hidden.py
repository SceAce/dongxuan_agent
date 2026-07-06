from __future__ import annotations

from .relations import element_relation


def attach_hidden_spirits(derived_lines: list[dict], hidden_spirits: list[dict]) -> None:
    by_position: dict[int, list[dict]] = {}
    for hidden in hidden_spirits:
        by_position.setdefault(hidden["position"], []).append(hidden)
    for line in derived_lines:
        line["hidden_spirits"] = list(by_position.get(line["position"], []))


def build_flying_hidden_analysis(hidden_spirits: list[dict], spirit_role_analysis: dict) -> dict:
    hidden_lines = []
    relations = []
    unresolved = []
    for hidden in hidden_spirits:
        item = {**hidden}
        item["hidden_role_impact"] = _role_impact(hidden["hidden_element"], spirit_role_analysis)
        item["flying_to_hidden_relation"] = element_relation(hidden["flying_element"], hidden["hidden_element"])
        item["hidden_to_flying_relation"] = element_relation(hidden["hidden_element"], hidden["flying_element"])
        item["flying_generates_hidden"] = item["flying_to_hidden_relation"] in {"generates", "same"}
        item["flying_controls_hidden"] = item["flying_to_hidden_relation"] == "controls"
        item["hidden_controls_flying"] = item["hidden_to_flying_relation"] == "controls"
        item["reason"] = _reason(item)
        hidden_lines.append(item)
        relations.append(_relation_summary(item))
    if spirit_role_analysis["status"] != "ready":
        unresolved.append("主用神链未定，飞伏只列伏神不作角色裁决。")
    return {
        "enabled": True,
        "scope": "飞伏只补缺失六亲与隐藏用神，不替代上卦用神和动变主线。",
        "hidden_lines": hidden_lines,
        "hidden_useful_gods": [
            item
            for item in hidden_lines
            if item["hidden_role_impact"] in {"supports_useful_god", "supports_original_spirit"}
        ],
        "relations": relations,
        "unresolved": unresolved,
    }


def completion_factors(flying_hidden_analysis: dict) -> dict:
    supporting = []
    blocking = []
    mixed = []
    for item in flying_hidden_analysis["hidden_lines"]:
        factor = {
            "line": item["position"],
            "hidden_six_relative": item["hidden_six_relative"],
            "hidden_element": item["hidden_element"],
            "flying_six_relative": item["flying_six_relative"],
            "flying_element": item["flying_element"],
            "summary": item["reason"],
        }
        role_key = _role_key(item)
        if item["hidden_role_impact"] in {"supports_useful_god", "supports_original_spirit"}:
            if item["flying_generates_hidden"]:
                supporting.append({**factor, "type": f"hidden_{role_key}_supported_by_flying"})
            elif item["flying_controls_hidden"]:
                blocking.append({**factor, "type": f"hidden_{role_key}_controlled_by_flying"})
            else:
                mixed.append({**factor, "type": f"hidden_{role_key}_present_but_buried"})
        elif item["hidden_role_impact"] in {"supports_avoiding_spirit", "supports_enemy_spirit"}:
            blocking.append({**factor, "type": f"hidden_{role_key}_supported"})
        else:
            mixed.append({**factor, "type": "hidden_role_unresolved"})
    return {"supporting_factors": supporting, "blocking_factors": blocking, "mixed_factors": mixed}


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


def _role_key(item: dict) -> str:
    return item["hidden_role_impact"].removeprefix("supports_")


def _reason(item: dict) -> str:
    role_name = {
        "supports_useful_god": "用神",
        "supports_original_spirit": "原神",
        "supports_avoiding_spirit": "忌神",
        "supports_enemy_spirit": "仇神",
        "neutral": "闲神",
        "mixed": "未定角色",
    }[item["hidden_role_impact"]]
    relation = {
        "same": "同类",
        "generates": "生伏神",
        "controls": "克伏神",
        "generated_by": "受伏神生",
        "controlled_by": "受伏神克",
        "none": "无直接生克",
    }[item["flying_to_hidden_relation"]]
    return (
        f"{item['name']}伏{item['hidden_six_relative']}{item['hidden_branch']}{item['hidden_element']}，"
        f"飞神为{item['flying_six_relative']}{item['flying_branch']}{item['flying_element']}，"
        f"飞伏关系为{relation}，伏神角色为{role_name}。"
    )


def _relation_summary(item: dict) -> dict:
    return {
        "position": item["position"],
        "hidden": f"{item['hidden_six_relative']}{item['hidden_branch']}{item['hidden_element']}",
        "flying": f"{item['flying_six_relative']}{item['flying_branch']}{item['flying_element']}",
        "flying_to_hidden_relation": item["flying_to_hidden_relation"],
        "hidden_to_flying_relation": item["hidden_to_flying_relation"],
        "hidden_role_impact": item["hidden_role_impact"],
    }
