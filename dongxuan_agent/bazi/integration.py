from __future__ import annotations

from .chart import HIDDEN_STEMS, BaziChart, ten_god
from ..constants import CONTROLLING, GENERATING, STEM_ELEMENTS


def build_integrated_analysis(
    chart: BaziChart,
    strength_analysis: dict,
    climate_analysis: dict,
    year_hints: dict,
) -> dict:
    payload = chart.to_dict()
    natal = _natal_structure(strength_analysis, climate_analysis)
    luck = _luck_influence(payload, strength_analysis, climate_analysis, year_hints.get("current_luck"))
    year = _year_influence(year_hints)
    integrated = _integrated_analysis(natal, luck, year, year_hints)
    return {
        "natal_structure": natal,
        "luck_influence": luck,
        "year_influence": year,
        "integrated_analysis": integrated,
        "uncertainty": [
            "三层合参 V1 用原局强弱调候、大运十神/气候作用、流年引动关系做结构化收敛；尚未纳入格局成败和用神定论。",
            "大运与流年的合化成败、三合三会成局、岁运并临细则仍需后续精校。",
        ],
    }


def _natal_structure(strength: dict, climate: dict) -> dict:
    day = strength["day_master_strength"]
    forces = strength["element_forces"]
    sorted_forces = sorted(
        forces.items(),
        key=lambda item: item[1]["effective_power"],
        reverse=True,
    )
    dominant = [element for element, force in sorted_forces if force["effective_power"] >= 2.0]
    weak = [element for element, force in sorted_forces if force["effective_power"] <= 0.8]
    if not dominant:
        dominant = [sorted_forces[0][0]]
    if not weak:
        weak = [sorted_forces[-1][0]]
    return {
        "day_master": day["day_master"],
        "day_element": day["day_element"],
        "day_master_level": day["level"],
        "strength_score": day["score"],
        "climate_profile": climate["season_profile"],
        "temperature": climate["temperature"],
        "moisture": climate["moisture"],
        "climate_need": climate["preferred_elements"],
        "dominant_forces": dominant,
        "weak_forces": weak,
        "root_summary": day["root_summary"],
        "structural_notes": [
            f"日主{day['day_master']}为{day['day_element']}，强弱为{day['level']}，评分 {day['score']}。",
            f"调候为{climate['temperature']}{climate['moisture']}，优先看 {'、'.join(climate['preferred_elements']) or '无明显单一调候'}。",
            f"有效力量较显者：{'、'.join(dominant)}；偏弱者：{'、'.join(weak)}。",
        ],
    }


def _luck_influence(payload: dict, strength: dict, climate: dict, current_luck: dict | None) -> dict:
    if not current_luck:
        return {
            "ganzhi": None,
            "supports_or_drains": "未提供性别或大运，无法定位当前大运。",
            "climate_effect": "未知",
            "ten_god_theme": [],
            "activated_palaces": [],
            "trend": "未纳入十年背景。",
        }
    day_master = payload["day_master"]
    day_element = STEM_ELEMENTS[day_master]
    gz = current_luck["ganzhi"]
    stem, branch = gz[0], gz[1]
    themes = [ten_god(day_master, stem)]
    themes.extend(ten_god(day_master, hidden) for hidden in HIDDEN_STEMS[branch])
    themes = _dedupe(themes)
    branch_element = STEM_ELEMENTS[HIDDEN_STEMS[branch][0]]
    supports = _element_supports_day(day_element, STEM_ELEMENTS[stem]) + _element_supports_day(day_element, branch_element)
    climate_effect = _climate_effect(stem + branch, climate)
    return {
        "ganzhi": gz,
        "virtual_age": current_luck.get("virtual_age"),
        "supports_or_drains": _support_label(supports),
        "climate_effect": climate_effect,
        "ten_god_theme": themes,
        "activated_palaces": [
            item for item in payload.get("branch_relationships", []) if branch in item["branches"]
        ],
        "trend": _luck_trend(themes, climate_effect, current_luck),
    }


def _year_influence(year_hints: dict) -> dict:
    flow = year_hints["flow_year"]
    return {
        "ganzhi": flow["ganzhi"],
        "visible_ten_god": flow["stem_ten_god"],
        "hidden_ten_gods": _dedupe(item["ten_god"] for item in flow["hidden_stems"]),
        "triggered_relations": year_hints.get("activated_relations", []),
        "activated_palaces": year_hints.get("activated_palaces", []),
        "event_candidates": year_hints.get("event_candidates", []),
        "event_trigger": _event_trigger(flow, year_hints.get("activated_relations", [])),
    }


def _integrated_analysis(natal: dict, luck: dict, year: dict, year_hints: dict) -> dict:
    visible = year["visible_ten_god"]
    relation_words = _relation_words(year["triggered_relations"])
    main_axis = _main_axis(visible, year["triggered_relations"])
    favorable = []
    pressure = []
    if any(item in natal["climate_need"] for item in ("火", "燥土")) and "巳" in (year["ganzhi"] or ""):
        favorable.append("流年巳火可回应原局寒湿调候需求。")
    if luck["climate_effect"] in {"加重寒湿", "加重燥热"}:
        pressure.append(f"大运{luck['ganzhi']}对调候作用为{luck['climate_effect']}。")
    if relation_words:
        pressure.append("流年触发 " + "、".join(relation_words) + "，事件感增强。")
    reasoning = [
        f"原局：{natal['day_master']}{natal['day_element']}强弱为{natal['day_master_level']}，{natal['climate_profile']}，调候取 {'、'.join(natal['climate_need']) or '中和'}。",
        f"原局根气：{natal['root_summary']}",
        f"大运：{luck['ganzhi']}，主题为{'、'.join(luck['ten_god_theme']) or '未定'}，对日主为{luck['supports_or_drains']}，调候作用为{luck['climate_effect']}。",
        f"流年：{year['ganzhi']}，天干为{visible}，藏干见{'、'.join(year['hidden_ten_gods'])}。",
    ]
    if relation_words:
        reasoning.append("流年引动：" + "、".join(relation_words) + "。")
    candidates = sorted(year_hints.get("event_candidates", []), key=lambda item: item["strength"], reverse=True)
    event_shape = _event_shape(main_axis, candidates)
    return {
        "main_axis": main_axis,
        "favorable_factors": favorable,
        "pressure_factors": pressure,
        "event_shape": event_shape,
        "reasoning_chain": reasoning,
        "avoid_overread": [
            "财星被引动不等于必有得财或恋爱，需结合现实问题与宫位反馈。",
            "刑害并临不等于灾祸，只表示触发、压力、牵制或反复。",
            "三层合参 V1 尚未给出格局/用神定论，不能把调候需求直接等同最终喜忌。",
        ],
    }


def _element_supports_day(day_element: str, other_element: str) -> int:
    if other_element == day_element:
        return 1
    if GENERATING[other_element] == day_element:
        return 1
    if GENERATING[day_element] == other_element:
        return -1
    if CONTROLLING[day_element] == other_element:
        return -1
    if CONTROLLING[other_element] == day_element:
        return -1
    return 0


def _support_label(score: int) -> str:
    if score > 0:
        return "扶助日主"
    if score < 0:
        return "克泄耗日主"
    return "扶耗并见"


def _climate_effect(ganzhi: str, climate: dict) -> str:
    elements = [STEM_ELEMENTS[ganzhi[0]], STEM_ELEMENTS[HIDDEN_STEMS[ganzhi[1]][0]]]
    if climate["temperature"] == "偏寒" and "水" in elements:
        return "加重寒湿"
    if climate["temperature"] == "偏寒" and "火" in elements:
        return "补暖局"
    if climate["temperature"] == "偏热" and "火" in elements:
        return "加重燥热"
    if climate["moisture"] == "偏燥" and "水" in elements:
        return "润燥"
    return "中性或需合全局"


def _luck_trend(themes: list[str], climate_effect: str, current_luck: dict) -> str:
    return f"{current_luck['ganzhi']}大运以{'、'.join(themes)}为主题，调候作用为{climate_effect}。"


def _event_trigger(flow: dict, relations: list[dict]) -> str:
    relation_text = "、".join(f"{item['field']}{item['type']}" for item in relations)
    if relation_text:
        return f"{flow['ganzhi']}以{flow['stem_ten_god']}外显，并由{relation_text}触发。"
    return f"{flow['ganzhi']}以{flow['stem_ten_god']}外显，未见强关系触发。"


def _relation_words(relations: list[dict]) -> list[str]:
    return _dedupe(f"{item['field']}{item['type']}" for item in relations)


def _main_axis(visible_ten_god: str, relations: list[dict]) -> str:
    palaces = _dedupe(item["palace"] for item in relations)
    palace_text = "、".join(palaces) if palaces else "原局"
    if "财" in visible_ten_god:
        return f"财星外显，引动{palace_text}"
    if visible_ten_god in {"正官", "七杀"}:
        return f"官杀外显，引动{palace_text}"
    if visible_ten_god in {"正印", "偏印"}:
        return f"印星外显，引动{palace_text}"
    if visible_ten_god in {"食神", "伤官"}:
        return f"食伤外显，引动{palace_text}"
    return f"{visible_ten_god}外显，引动{palace_text}"


def _event_shape(main_axis: str, candidates: list[dict]) -> str:
    if not candidates:
        return main_axis
    primary = candidates[0]["domain"]
    return f"{main_axis}，优先落在{primary}这一类事件形态。"


def _dedupe(values) -> list:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
