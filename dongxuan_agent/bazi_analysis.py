from __future__ import annotations

from datetime import datetime
from typing import Any

from .bazi import BRANCH_COMBINE, BRANCH_HARM, HIDDEN_STEMS, BaziChart, ten_god
from .constants import BRANCH_OPPOSITE, BRANCH_PUNISH
from .divination import year_ganzhi


PILLAR_BRANCH_FIELDS = {
    "年柱": "年支",
    "月柱": "月支",
    "日柱": "日支",
    "时柱": "时支",
}

PALACE_MEANINGS = {
    "年支": "家庭/长辈/早年环境",
    "月支": "学业/规则/社会环境",
    "日支": "自身状态/关系宫位",
    "时支": "计划/输出/晚辈事项",
    "大运支": "十年背景主题",
}


def build_year_analysis_hints(chart: BaziChart, target_year: int) -> dict:
    payload = chart.to_dict()
    target_ganzhi = year_ganzhi(target_year)
    flow_stem, flow_branch = target_ganzhi[0], target_ganzhi[1]
    day_master = payload["day_master"]
    current_luck = _current_luck(payload, target_year)
    flow_year = {
        "ganzhi": target_ganzhi,
        "stem": flow_stem,
        "branch": flow_branch,
        "stem_ten_god": ten_god(day_master, flow_stem),
        "hidden_stems": [
            {"stem": stem, "ten_god": ten_god(day_master, stem)}
            for stem in HIDDEN_STEMS[flow_branch]
        ],
    }
    activated_relations = _activated_relations(payload, flow_branch, current_luck)
    activated_palaces = _activated_palaces(activated_relations)
    event_candidates = _event_candidates(payload, flow_year, current_luck, activated_relations, activated_palaces)
    return {
        "target_year": target_year,
        "year_ganzhi": target_ganzhi,
        "current_luck": current_luck,
        "flow_year": flow_year,
        "activated_relations": activated_relations,
        "activated_palaces": activated_palaces,
        "event_candidates": event_candidates,
        "conflicts": _conflicts(event_candidates, activated_relations),
    }


def _current_luck(payload: dict, target_year: int) -> dict | None:
    luck = payload.get("luck") or {}
    cycles = luck.get("cycles") or []
    if not cycles:
        return None
    birth_year = datetime.fromisoformat(payload["calendar"]["datetime"]).year
    virtual_age = target_year - birth_year + 1
    for cycle in cycles:
        if cycle["start_age_years"] <= virtual_age < cycle["end_age_years"]:
            return {
                **cycle,
                "virtual_age": virtual_age,
                "match_rule": "按目标年虚岁落入大运 start_age_years/end_age_years 区间匹配。",
            }
    return {
        **cycles[-1],
        "virtual_age": virtual_age,
        "match_rule": "目标年虚岁超出已列大运，回退到最后一个已知大运。",
    }


def _activated_relations(payload: dict, flow_branch: str, current_luck: dict | None) -> list[dict]:
    targets = [
        {
            "field": f"流年支与{PILLAR_BRANCH_FIELDS[pillar['name']]}",
            "palace": PILLAR_BRANCH_FIELDS[pillar["name"]],
            "branch": pillar["branch"],
            "ganzhi": pillar["ganzhi"],
        }
        for pillar in payload["pillars"]
    ]
    if current_luck:
        luck_ganzhi = current_luck["ganzhi"]
        targets.append({
            "field": "流年支与大运支",
            "palace": "大运支",
            "branch": luck_ganzhi[1],
            "ganzhi": luck_ganzhi,
        })

    relations: list[dict] = []
    for target in targets:
        for relation_type, note in _branch_relation_types(flow_branch, target["branch"]):
            relations.append({
                "field": target["field"],
                "type": relation_type,
                "branches": _branch_pair(flow_branch, target["branch"]),
                "flow_branch": flow_branch,
                "target_branch": target["branch"],
                "target_ganzhi": target["ganzhi"],
                "palace": target["palace"],
                "evidence": note,
            })
    return relations


def _branch_relation_types(left: str, right: str) -> list[tuple[str, str]]:
    relations: list[tuple[str, str]] = []
    if left == right:
        relations.append(("并临", f"{left} 与 {right} 同支，形成伏吟/并临式触发。"))
    if BRANCH_OPPOSITE[left] == right:
        relations.append(("冲", f"{left}{right} 为六冲，主变化触发。"))
    combine_element = BRANCH_COMBINE.get(frozenset((left, right)))
    if combine_element:
        relations.append(("合", f"{left}{right} 六合，合化取象为{combine_element}。"))
    if frozenset((left, right)) in BRANCH_HARM:
        relations.append(("害", f"{left}{right} 为六害，提示关系牵制。"))
    if BRANCH_PUNISH.get(left) == right or BRANCH_PUNISH.get(right) == left:
        relation_type = "自刑" if left == right else "刑"
        relations.append((relation_type, f"{left}{right} 构成地支刑动，需合全局收敛。"))
    return relations


def _activated_palaces(activated_relations: list[dict]) -> list[dict]:
    by_palace: dict[str, dict[str, Any]] = {}
    for relation in activated_relations:
        palace = relation["palace"]
        item = by_palace.setdefault(
            palace,
            {
                "palace": palace,
                "meaning": PALACE_MEANINGS.get(palace, "待结合原局解释"),
                "relations": [],
                "evidence": [],
            },
        )
        item["relations"].append(relation["type"])
        item["evidence"].append(f"{relation['field']} {relation['type']}")
    return list(by_palace.values())


def _event_candidates(
    payload: dict,
    flow_year: dict,
    current_luck: dict | None,
    activated_relations: list[dict],
    activated_palaces: list[dict],
) -> list[dict]:
    flow_ten_gods = {flow_year["stem_ten_god"], *(item["ten_god"] for item in flow_year["hidden_stems"])}
    luck_ten_gods = _luck_ten_gods(payload, current_luck)
    all_ten_gods = flow_ten_gods | luck_ten_gods
    activated_palace_names = {item["palace"] for item in activated_palaces}
    has_change_relation = any(item["type"] in {"冲", "刑", "自刑", "害", "并临"} for item in activated_relations)
    candidates = [
        _candidate(
            "学业/考试/规则压力",
            _score(all_ten_gods, {"正印", "偏印", "正官", "七杀", "食神", "伤官"}) + _palace_score(activated_palace_names, {"月支"}),
            _evidence(
                "流年/大运见印、官杀或食伤，适合落在学业、考试、证书、规则压力取象。",
                flow_year,
                current_luck,
                activated_relations,
                {"月支"},
            ),
        ),
        _candidate(
            "财务/资源/男命关系议题",
            _score(all_ten_gods, {"正财", "偏财", "比肩", "劫财", "食神", "伤官"}) + (1 if payload.get("gender") == "男" else 0),
            _evidence(
                "流年/大运见财星或生财、竞争相关十神；男命财星兼作关系议题提示。",
                flow_year,
                current_luck,
                activated_relations,
                {"日支"},
            ),
        ),
        _candidate(
            "状态变化/环境触发",
            len(activated_relations) + (2 if has_change_relation else 0),
            _evidence(
                "流年支触发原局或大运支，优先作为环境变化、状态切换和事件触发点。",
                flow_year,
                current_luck,
                activated_relations,
                activated_palace_names,
            ),
        ),
    ]
    return [item for item in candidates if item["strength"] > 0]


def _luck_ten_gods(payload: dict, current_luck: dict | None) -> set[str]:
    if not current_luck:
        return set()
    day_master = payload["day_master"]
    ganzhi = current_luck["ganzhi"]
    return {
        ten_god(day_master, ganzhi[0]),
        *(ten_god(day_master, stem) for stem in HIDDEN_STEMS[ganzhi[1]]),
    }


def _candidate(domain: str, strength: int, evidence: list[str]) -> dict:
    return {
        "domain": domain,
        "strength": strength,
        "evidence": evidence,
    }


def _score(actual: set[str], expected: set[str]) -> int:
    return len(actual & expected)


def _palace_score(actual: set[str], expected: set[str]) -> int:
    return len(actual & expected) * 2


def _evidence(
    note: str,
    flow_year: dict,
    current_luck: dict | None,
    activated_relations: list[dict],
    palaces: set[str],
) -> list[str]:
    evidence = [
        note,
        f"流年{flow_year['ganzhi']}：天干十神 {flow_year['stem_ten_god']}，藏干十神 "
        f"{'、'.join(item['stem'] + ':' + item['ten_god'] for item in flow_year['hidden_stems'])}。",
    ]
    if current_luck:
        evidence.append(f"当前大运 {current_luck['ganzhi']}，虚岁 {current_luck['virtual_age']}。")
    matched = [
        f"{item['field']} {item['type']}"
        for item in activated_relations
        if item["palace"] in palaces
    ]
    if matched:
        evidence.append("宫位触发：" + "、".join(matched))
    return evidence


def _conflicts(event_candidates: list[dict], activated_relations: list[dict]) -> list[str]:
    conflicts = [
        "候选事件域偏多时，应先按原局结构、大运背景、流年触发强弱收敛，不可并列输出过多结论。",
        "刑动不可单独定凶；冲、刑、害、并临只代表触发方式，需结合十神、宫位和现实背景。",
    ]
    if len(event_candidates) > 2:
        conflicts.append("当前存在三个以上候选域，最终分析应选择一个主象，最多保留一个副象。")
    if any(item["type"] in {"刑", "自刑"} for item in activated_relations):
        conflicts.append("出现刑/自刑时只提示压力或动作，不直接等同病灾、破财或关系破裂。")
    return conflicts


def _branch_pair(left: str, right: str) -> str:
    if left == right:
        return left + right
    from .constants import BRANCHES

    return "".join(sorted((left, right), key=BRANCHES.index))
