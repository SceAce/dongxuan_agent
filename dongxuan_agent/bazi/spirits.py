from __future__ import annotations

from typing import Any

from ..constants import DAY_NOBLEMAN, STEM_LODGING_BRANCH


WENCHANG = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}

XUETANG_V1 = {
    "甲": "亥", "乙": "午", "丙": "寅", "丁": "酉", "戊": "寅",
    "己": "酉", "庚": "巳", "辛": "子", "壬": "申", "癸": "卯",
}

YANGREN = {
    "甲": "卯", "乙": "寅", "丙": "午", "丁": "巳", "戊": "午",
    "己": "巳", "庚": "酉", "辛": "申", "壬": "子", "癸": "亥",
}

THREE_HARMONY_SPIRITS = {
    ("寅", "午", "戌"): {"驿马": "申", "桃花": "卯", "华盖": "戌", "将星": "午"},
    ("申", "子", "辰"): {"驿马": "寅", "桃花": "酉", "华盖": "辰", "将星": "子"},
    ("巳", "酉", "丑"): {"驿马": "亥", "桃花": "午", "华盖": "丑", "将星": "酉"},
    ("亥", "卯", "未"): {"驿马": "巳", "桃花": "子", "华盖": "未", "将星": "卯"},
}

TIANDE_BY_MONTH_BRANCH = {
    "寅": "丁", "卯": "申", "辰": "壬", "巳": "辛", "午": "亥", "未": "甲",
    "申": "癸", "酉": "寅", "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚",
}

YUEDE_BY_MONTH_BRANCH = {
    "寅": "丙", "午": "丙", "戌": "丙",
    "申": "壬", "子": "壬", "辰": "壬",
    "亥": "甲", "卯": "甲", "未": "甲",
    "巳": "庚", "酉": "庚", "丑": "庚",
}

SUPPORTS = {
    "文昌": ["文本表达", "教育训练", "信息处理"],
    "学堂": ["教育训练", "人文研究", "研究专精"],
    "华盖": ["研究专精", "人文研究", "艺术设计"],
    "驿马": ["跨域迁移", "公共传播"],
    "桃花": ["公共传播", "艺术设计", "文本表达"],
    "天乙贵人": ["教育训练", "制度法理"],
    "天德": ["教育训练", "制度法理"],
    "月德": ["教育训练", "制度法理"],
    "禄神": ["资源经营", "工程系统"],
    "将星": ["制度法理", "资源经营", "工程系统"],
    "羊刃": ["技能输出", "工程系统"],
}

AVOID = {
    "文昌": "文昌只增强文书学习象，不直接等同文科专业。",
    "学堂": "学堂只增强学历训练和学术承载，不直接等同高学历或师范。",
    "华盖": "华盖只增强研究专精，可偏人文、技术或艺术，不能单独定专业。",
    "驿马": "驿马只增强迁移、平台和跨域象，不直接等同出国、交通或外语。",
    "桃花": "桃花只增强表达、人际、审美和受众连接，不直接等同传媒或艺术。",
    "天乙贵人": "天乙贵人只作助力和转圜，不保证录取、上岸或贵人帮助。",
    "天德": "天德只作缓和和助力，不替代结构证据。",
    "月德": "月德只作缓和和助力，不替代结构证据。",
    "禄神": "禄神只增强资源承载和落地性，不直接等同职位或收入。",
    "将星": "将星只增强组织执行和规则场景，不直接等同管理者或军警。",
    "羊刃": "羊刃增强竞争和执行强度，也提示冲突风险，不直接定凶吉。",
}

SCORING_POLICY = "神煞为辅助加权，总贡献受上限约束，不能覆盖强弱、格局、病药。"


def build_bazi_spirit_sha_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        chart_payload = _chart_payload(payload)
        rules = _spirit_rules(chart_payload)
        positions = _positions(payload, chart_payload)
        active = [_active_hit(rule, positions) for rule in rules]
        active = [item for item in active if item["hit_positions"]]
        return {
            "active": active,
            "scoring_policy": SCORING_POLICY,
            "uncertainty": [
                "八字神煞 V1 只覆盖专业/职业识别相关神煞，且只作中间画像辅助加权。",
                "学堂、天德、月德等神煞存在派别差异，V1 输出规则来源字段并保留不确定项。",
            ],
        }
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return {
            "active": [],
            "scoring_policy": SCORING_POLICY,
            "uncertainty": [f"八字神煞计算失败，已跳过神煞辅助：{exc}"],
        }


def _chart_payload(payload: dict[str, Any]) -> dict[str, Any]:
    chart = payload.get("chart") or payload
    return _dict_or_empty(chart)


def _spirit_rules(payload: dict[str, Any]) -> list[dict[str, str]]:
    day_master = payload["day_master"]
    day_branch = _pillar(payload, "日柱")["branch"]
    month_branch = _pillar(payload, "月柱")["branch"]
    harmony = _three_harmony_rule(day_branch)
    return [
        _rule("文昌", WENCHANG[day_master], "branch", "day_stem"),
        _rule("学堂", XUETANG_V1[day_master], "branch", "day_stem"),
        _rule("禄神", STEM_LODGING_BRANCH[day_master], "branch", "day_stem"),
        _rule("羊刃", YANGREN[day_master], "branch", "day_stem"),
        _rule("驿马", harmony["驿马"], "branch", "day_branch"),
        _rule("桃花", harmony["桃花"], "branch", "day_branch"),
        _rule("华盖", harmony["华盖"], "branch", "day_branch"),
        _rule("将星", harmony["将星"], "branch", "day_branch"),
        *(_rule("天乙贵人", item, "branch", "day_stem") for item in DAY_NOBLEMAN[day_master]),
        _rule("天德", TIANDE_BY_MONTH_BRANCH[month_branch], _value_type(TIANDE_BY_MONTH_BRANCH[month_branch]), "month_branch"),
        _rule("月德", YUEDE_BY_MONTH_BRANCH[month_branch], "stem", "month_branch"),
    ]


def _rule(name: str, value: str, value_type: str, basis: str) -> dict[str, str]:
    return {"name": name, "value": value, "value_type": value_type, "basis": basis}


def _value_type(value: str) -> str:
    return "stem" if value in "甲乙丙丁戊己庚辛壬癸" else "branch"


def _positions(payload: dict[str, Any], chart_payload: dict[str, Any]) -> list[dict[str, str]]:
    positions = []
    for pillar in chart_payload.get("pillars", []):
        positions.append({"location": pillar["name"] + "干", "value": pillar["stem"], "value_type": "stem"})
        positions.append({"location": pillar["name"] + "支", "value": pillar["branch"], "value_type": "branch"})
    analysis_hints = _dict_or_empty(payload.get("analysis_hints"))
    current_luck = _dict_or_empty(analysis_hints.get("current_luck"))
    if current_luck.get("ganzhi"):
        positions.append({"location": "当前大运干", "value": current_luck["ganzhi"][0], "value_type": "stem"})
        positions.append({"location": "当前大运支", "value": current_luck["ganzhi"][1], "value_type": "branch"})
    flow_year = _dict_or_empty(analysis_hints.get("flow_year"))
    if flow_year.get("ganzhi"):
        positions.append({"location": "目标流年干", "value": flow_year["ganzhi"][0], "value_type": "stem"})
        positions.append({"location": "目标流年支", "value": flow_year["ganzhi"][1], "value_type": "branch"})
    return positions


def _dict_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    raise TypeError(f"expected dict payload section, got {type(value).__name__}")


def _active_hit(rule: dict[str, str], positions: list[dict[str, str]]) -> dict[str, Any]:
    hits = [
        item["location"]
        for item in positions
        if item["value_type"] == rule["value_type"] and item["value"] == rule["value"]
    ]
    strength = _hit_strength(hits)
    return {
        **rule,
        "hit_positions": hits,
        "strength": strength,
        "score_delta": {"strong": 0.2, "medium": 0.15, "weak": 0.08}[strength],
        "supports": SUPPORTS[rule["name"]],
        "avoid": AVOID[rule["name"]],
        "evidence": [
            {
                "source_field": "chart.pillars/analysis_hints",
                "source_value": {"value": rule["value"], "hit_positions": hits},
                "rule": f"{rule['name']}按{rule['basis']}取{rule['value']}，命中关键位置才辅助加权。",
                "text": f"{rule['name']}命中{'、'.join(hits) if hits else '无关键位置'}。",
            }
        ],
    }


def _hit_strength(hits: list[str]) -> str:
    strong_positions = {
        "日柱支", "日柱干", "月柱支", "月柱干",
        "当前大运支", "当前大运干", "目标流年支", "目标流年干",
    }
    if any(item in strong_positions for item in hits):
        return "strong"
    if any(item in {"年柱支", "年柱干", "时柱支", "时柱干"} for item in hits):
        return "medium"
    return "weak"


def _pillar(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for pillar in payload["pillars"]:
        if pillar["name"] == name:
            return pillar
    raise KeyError(name)


def _three_harmony_rule(branch: str) -> dict[str, str]:
    for group, rule in THREE_HARMONY_SPIRITS.items():
        if branch in group:
            return rule
    raise ValueError(branch)
