from __future__ import annotations

from .chart import BaziChart


SEASON_PROFILES = {
    "亥": {"profile": "亥月寒水渐旺", "temperature_bias": -1.4, "moisture_bias": 1.2},
    "子": {"profile": "子月寒水当令", "temperature_bias": -1.8, "moisture_bias": 1.5},
    "丑": {"profile": "丑月寒湿土", "temperature_bias": -1.5, "moisture_bias": 1.1},
    "寅": {"profile": "寅月木气初升渐温", "temperature_bias": -0.3, "moisture_bias": 0.3},
    "卯": {"profile": "卯月木旺温和", "temperature_bias": 0.1, "moisture_bias": 0.2},
    "辰": {"profile": "辰月湿土蓄水", "temperature_bias": 0.0, "moisture_bias": 0.8},
    "巳": {"profile": "巳月火起渐热", "temperature_bias": 1.2, "moisture_bias": -0.7},
    "午": {"profile": "午月火热当令", "temperature_bias": 1.8, "moisture_bias": -1.2},
    "未": {"profile": "未月暑土偏燥", "temperature_bias": 1.2, "moisture_bias": -0.7},
    "申": {"profile": "申月金旺渐燥", "temperature_bias": 0.2, "moisture_bias": -0.6},
    "酉": {"profile": "酉月燥金当令", "temperature_bias": 0.0, "moisture_bias": -1.0},
    "戌": {"profile": "戌月燥土收火", "temperature_bias": 0.4, "moisture_bias": -1.1},
}


def analyze_climate(chart: BaziChart, strength_analysis: dict | None = None) -> dict:
    payload = chart.to_dict()
    month_branch = next(item for item in payload["pillars"] if item["name"] == "月柱")["branch"]
    strength = strength_analysis or {}
    forces = strength.get("element_forces") or {}
    profile = SEASON_PROFILES[month_branch]

    fire = _power(forces, "火")
    water = _power(forces, "水")
    wood = _power(forces, "木")
    metal = _power(forces, "金")
    earth = _power(forces, "土")
    temperature_score = profile["temperature_bias"] + fire * 0.22 + wood * 0.06 - water * 0.2 - metal * 0.05
    moisture_score = profile["moisture_bias"] + water * 0.2 + wood * 0.04 - fire * 0.16 - metal * 0.07

    preferred_elements = []
    if temperature_score < -0.4:
        preferred_elements.extend(["火", "燥土"])
    elif temperature_score > 0.4:
        preferred_elements.extend(["水", "金"])
    if moisture_score > 0.45 and "燥土" not in preferred_elements:
        preferred_elements.append("燥土")
    elif moisture_score < -0.45 and "水" not in preferred_elements:
        preferred_elements.append("水")

    evidence = [
        profile["profile"],
        f"按有效力量看：火 {round(fire, 3)}、水 {round(water, 3)}、土 {round(earth, 3)}、金 {round(metal, 3)}、木 {round(wood, 3)}。",
    ]
    branches = "".join(item["branch"] for item in payload["pillars"])
    if "巳" in branches and "午" in branches:
        evidence.append("原局见巳午火，可暖局，但需结合火的有效力量与根气受损情况。")
    elif fire > 0:
        evidence.append("原局有火，可缓解寒象，但力度以有效力量为准。")

    excess_elements = [
        element
        for element, power in {"火": fire, "水": water, "土": earth, "金": metal, "木": wood}.items()
        if power >= 3.0
    ]

    return {
        "season_profile": profile["profile"],
        "temperature": _temperature_level(temperature_score),
        "moisture": _moisture_level(moisture_score),
        "temperature_score": round(temperature_score, 3),
        "moisture_score": round(moisture_score, 3),
        "preferred_elements": preferred_elements,
        "excess_elements": excess_elements,
        "evidence": evidence,
        "uncertainty": [
            "调候 V1 以月令寒暖燥湿为主，结合五行有效力量修正；尚未细分十干调候专论。",
            "土的燥湿 V1 先由月令和支类概括，未细分每个藏干透出后的燥湿转换。",
        ],
    }


def _power(forces: dict, element: str) -> float:
    return float((forces.get(element) or {}).get("effective_power") or 0.0)


def _temperature_level(score: float) -> str:
    if score <= -0.4:
        return "偏寒"
    if score >= 0.4:
        return "偏热"
    return "中和"


def _moisture_level(score: float) -> str:
    if score <= -0.45:
        return "偏燥"
    if score >= 0.45:
        return "偏湿"
    return "中和"
