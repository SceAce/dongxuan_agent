from __future__ import annotations

from .chart import HIDDEN_STEMS, BaziChart
from ..constants import STEM_ELEMENTS


def analyze_luck_year_remedy(chart: BaziChart, remedy_analysis: dict, god_candidates: dict, year_hints: dict) -> dict:
    current_luck = year_hints.get("current_luck")
    flow_year = year_hints["flow_year"]
    luck_effect = _luck_effect(current_luck, remedy_analysis, god_candidates)
    year_effect = _year_effect(flow_year, remedy_analysis, god_candidates, year_hints)
    combined = _combined_effect(luck_effect["effect"], year_effect["effect"])
    return {
        "luck_effect_on_remedy": luck_effect,
        "year_effect_on_remedy": year_effect,
        "combined_effect": combined,
        "reasoning_chain": [
            _luck_reason(luck_effect),
            _year_reason(year_effect),
            f"综合判断为{combined}：以候选病药为轴，不把候选用神说成最终用神。",
        ],
        "uncertainty": [
            "岁运药病 V1 只判断大运/流年五行对候选病药的方向，不细判合化成败和格局高低。",
            "来药不等于必吉，加病不等于必凶，仍需结合事件领域和现实背景。",
        ],
    }


def _luck_effect(current_luck: dict | None, remedy: dict, gods: dict) -> dict:
    if not current_luck:
        return {"ganzhi": None, "effect": "未知", "evidence": ["未提供性别或未定位大运。"]}
    gz = current_luck["ganzhi"]
    elements = _ganzhi_elements(gz)
    return _effect_payload(gz, elements, remedy, gods)


def _year_effect(flow_year: dict, remedy: dict, gods: dict, year_hints: dict) -> dict:
    gz = flow_year["ganzhi"]
    elements = [STEM_ELEMENTS[flow_year["stem"]]]
    elements.extend(STEM_ELEMENTS[item["stem"]] for item in flow_year["hidden_stems"])
    payload = _effect_payload(gz, elements, remedy, gods)
    if any(item["type"] in {"刑", "害", "冲"} for item in year_hints.get("activated_relations", [])):
        payload["evidence"].append("流年同时触发刑害冲，来药也带压力或反复。")
        if payload["effect"] == "来药":
            payload["effect"] = "药病并见"
    return payload


def _effect_payload(gz: str, elements: list[str], remedy: dict, gods: dict) -> dict:
    usable = set(_normalize_element(item) for item in remedy.get("usable_gods", []))
    avoid = set(_normalize_element(item) for item in remedy.get("avoid_gods", []))
    normalized = [_normalize_element(item) for item in elements]
    has_medicine = any(item in usable for item in normalized)
    has_problem = any(item in avoid for item in normalized)
    if has_medicine and has_problem:
        effect = "药病并见"
    elif has_medicine:
        effect = "来药"
    elif has_problem:
        effect = "加病"
    else:
        effect = "中性"
    return {
        "ganzhi": gz,
        "elements": elements,
        "effect": effect,
        "evidence": [
            f"{gz}五行触及：{'、'.join(elements)}。",
            f"候选药：{'、'.join(remedy.get('usable_gods', [])) or '无'}；候选忌：{'、'.join(remedy.get('avoid_gods', [])) or '无'}。",
        ],
    }


def _ganzhi_elements(gz: str) -> list[str]:
    # 岁运药病 V1 只以天干与地支本气定主方向；中余气仅作后续精校，
    # 避免把寅中丙火之类弱线索误判成明确来药。
    return [STEM_ELEMENTS[gz[0]], STEM_ELEMENTS[HIDDEN_STEMS[gz[1]][0]]]


def _normalize_element(value: str) -> str:
    if value in {"燥土", "湿土"}:
        return "土"
    if value in {"财", "官", "印"}:
        return value
    return value


def _combined_effect(luck_effect: str, year_effect: str) -> str:
    effects = {luck_effect, year_effect}
    if "药病并见" in effects:
        return "药病并见"
    if "来药" in effects and "加病" in effects:
        return "药病并见"
    if "来药" in effects:
        return "来药"
    if "加病" in effects:
        return "加病"
    if "未知" in effects:
        return "未知"
    return "中性"


def _luck_reason(effect: dict) -> str:
    return f"大运{effect['ganzhi']}对病药作用为{effect['effect']}：{'；'.join(effect['evidence'])}"


def _year_reason(effect: dict) -> str:
    return f"流年{effect['ganzhi']}对病药作用为{effect['effect']}：{'；'.join(effect['evidence'])}"
