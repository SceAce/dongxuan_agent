from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


WIKI_ROOT = Path("/home/source/Documents/东玄知识库/wiki")
SYMBOLIC_LAYERS_PATH = WIKI_ROOT / "structured" / "bazi_symbolic_layers.json"


QUESTION_KEYWORDS = {
    "专业/职业识别": ("专业", "职业", "行业", "工作方向", "学什么", "读什么", "干什么", "就业方向"),
    "学业/考试/竞赛": ("学业", "考试", "证书", "申请", "竞赛", "成绩", "录取", "升学", "课程"),
    "资源/目标/关系": ("财", "钱", "资源", "关系", "对象", "恋爱", "合作", "机会"),
    "技术/项目/竞赛": ("技术", "项目", "代码", "软件", "网络", "安全", "CTF", "开发", "训练"),
    "迁移/环境变化": ("搬", "迁移", "出行", "换环境", "转学", "实习", "工作"),
}


def build_imagery_analysis(payload: dict) -> dict:
    question = payload.get("question") or ""
    domain = _question_domain(question, payload)
    context = _context_frame(payload)
    candidates = _candidate_images(payload, domain, context)
    candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)
    main = candidates[0] if candidates else _empty_image()
    secondary = _secondary_image(candidates, main)
    return {
        "question_domain": domain,
        "context_frame": context,
        "symbol_sources": _symbol_sources(payload),
        "candidate_images": candidates,
        "main_image": main,
        "secondary_image": secondary,
        "answer_guidance": _answer_guidance(payload, domain, main, secondary),
        "avoid_images": [
            "不能仅凭财星直接断恋爱或得财，必须结合日支、问题背景和岁运引动。",
            "不能仅凭官杀直接断灾祸或上岸，必须结合格局、药病和现实目标。",
            "识别专业、职业、行业时必须先形成抽象取象画像，再给最多两个现实落点；不得罗列候选清单。",
            "识别专业、职业、行业时必须先看月令季节力量、有效力量、干支作用和强弱证据，不得把五行或十神直接等同于现实专业。",
            "取象 V1 只做现代语境映射和证据收敛，不替代用户现实反馈。",
        ],
        "reasoning_chain": _reasoning_chain(payload, main, secondary),
        "uncertainty": [
            "取象 V1 输出抽象取象画像和知识库检索词，并要求每条象都有 JSON 字段证据；知识库实体页仍以索引为主，精细象义需继续结晶化。",
            "现代背景只按出生年、目标年、问题词和命盘字段推断阶段，不把推断当作已确认事实。",
        ],
    }


def _question_domain(question: str, payload: dict) -> str:
    for domain, keywords in QUESTION_KEYWORDS.items():
        if any(keyword in question for keyword in keywords):
            return domain
    if payload.get("analysis_hints"):
        return "year_event"
    return "general_year"


def _context_frame(payload: dict) -> dict:
    calendar = payload["chart"]["calendar"] if "chart" in payload else payload["calendar"]
    birth_year = datetime.fromisoformat(calendar["datetime"]).year
    target_year = (payload.get("analysis_hints") or {}).get("target_year")
    virtual_age = target_year - birth_year + 1 if target_year else None
    if virtual_age is not None and 18 <= virtual_age <= 24:
        age_stage = "大学/训练期"
        modern_context = ["课程", "项目", "竞赛", "证书", "技术实践", "实习准备"]
    elif virtual_age is not None and 25 <= virtual_age <= 35:
        age_stage = "职业建立期"
        modern_context = ["工作", "项目", "收入", "合作", "职业转换"]
    else:
        age_stage = "未定阶段"
        modern_context = ["学习", "工作", "家庭", "关系", "资源"]
    evidence = []
    if virtual_age is not None:
        evidence.append(_evidence("analysis_hints.current_luck.virtual_age", virtual_age, "按目标年虚岁判断现代阶段", f"目标年虚岁 {virtual_age}，优先映射到{age_stage}。"))
    return {
        "age_stage": age_stage,
        "modern_context": modern_context,
        "evidence": evidence,
    }


def _candidate_images(payload: dict, domain: str, context: dict) -> list[dict]:
    candidates = []
    candidates.extend(_pattern_images(payload))
    candidates.extend(_year_images(payload))
    candidates.extend(_remedy_images(payload))
    candidates.extend(_relation_images(payload))
    _apply_context_bias(candidates, domain, context)
    return [item for item in candidates if item["evidence"]]


def _pattern_images(payload: dict) -> list[dict]:
    pattern = payload["pattern_analysis"]
    primary = pattern["primary_pattern"]
    images = []
    if primary["name"] in {"食神格", "伤官格"}:
        images.append(_image(
            "技术/项目/竞赛",
            "食伤格局主输出、表达、作品、技能训练；现代语境下优先落到技术实践、项目、竞赛或作品产出。",
            4,
            [
                _evidence("pattern_analysis.primary_pattern", primary["name"], "格局现代取象", f"主候选格局为{primary['name']}。"),
                _evidence("pattern_analysis.formation_evidence", pattern["formation_evidence"], "月令取格证据", "格局证据：" + "；".join(pattern["formation_evidence"])),
            ],
        ))
    if primary["name"] in {"正官格", "七杀格"}:
        images.append(_image("学业/考试/竞赛", "官杀格局主规则、考核、压力、资格。", 3, [_evidence("pattern_analysis.primary_pattern", primary["name"], "格局现代取象", f"主候选格局为{primary['name']}。")]))
    return images


def _year_images(payload: dict) -> list[dict]:
    hints = payload.get("analysis_hints") or {}
    flow = hints.get("flow_year") or {}
    integration = payload.get("integrated_analysis") or {}
    integrated = integration.get("integrated_analysis") or {}
    candidates = []
    visible = flow.get("stem_ten_god")
    if visible and "财" in visible:
        candidates.append(_image(
            "资源/目标/关系",
            "财星外显，现代语境优先取资源、目标、机会、合作与关系议题；男命可带感情线索但不单独定恋爱。",
            4,
            [
                _evidence("analysis_hints.flow_year.stem_ten_god", visible, "十神取象", f"流年天干十神为{visible}。"),
                _evidence("integrated_analysis.integrated_analysis.main_axis", integrated.get("main_axis"), "三层合参主轴", f"三层合参主轴：{integrated.get('main_axis')}。"),
            ],
        ))
    event_shape = integrated.get("event_shape")
    if event_shape:
        candidates.append(_image(
            "状态变化/环境触发",
            "流年引动自身或大运支，取状态变化、阶段切换、事件触发。",
            3,
            [_evidence("integrated_analysis.integrated_analysis.event_shape", event_shape, "三层合参事件形态", event_shape)],
        ))
    return candidates


def _remedy_images(payload: dict) -> list[dict]:
    luck_year = payload.get("luck_year_remedy") or {}
    remedy = payload.get("remedy_analysis") or {}
    if not luck_year:
        return []
    return [
        _image(
            "压力中有转机",
            "大运加病、流年来药或药病并见，取压力牵制中出现可用机会，但过程反复。",
            3,
            [
                _evidence("remedy_analysis.priority", remedy.get("priority"), "病药优先级", f"病药优先级为{remedy.get('priority')}。"),
                _evidence("luck_year_remedy.combined_effect", luck_year.get("combined_effect"), "岁运药病", f"岁运药病综合为{luck_year.get('combined_effect')}。"),
            ],
        )
    ]


def _relation_images(payload: dict) -> list[dict]:
    hints = payload.get("analysis_hints") or {}
    relations = hints.get("activated_relations") or []
    if not relations:
        return []
    relation_text = "、".join(f"{item['field']}{item['type']}" for item in relations)
    domains = {item.get("palace") for item in relations}
    score = 3 + (1 if "日支" in domains else 0)
    return [
        _image(
            "自身状态/关系宫位被触发",
            "流年触及日支或大运支，取自身状态、关系宫位、阶段主题被引动。",
            score,
            [_evidence("analysis_hints.activated_relations", relations, "宫位引动取象", f"引动关系：{relation_text}。")],
        )
    ]


def _apply_context_bias(candidates: list[dict], domain: str, context: dict) -> None:
    for item in candidates:
        if domain == "学业/考试/竞赛" and item["domain"] in {"学业/考试/竞赛", "技术/项目/竞赛"}:
            item["score"] += 3
            item["evidence"].append(_evidence("question", domain, "问题领域偏置", "用户问题指向学业/考试/竞赛，优先收敛到学习训练相关主象。"))
        elif domain == "技术/项目/竞赛" and item["domain"] == "技术/项目/竞赛":
            item["score"] += 3
            item["evidence"].append(_evidence("question", domain, "问题领域偏置", "用户问题指向技术/项目/竞赛，优先收敛到技术实践。"))
        elif domain == "专业/职业识别" and item["domain"] in {"技术/项目/竞赛", "学业/考试/竞赛"}:
            item["score"] += 2
            item["evidence"].append(_evidence("question", domain, "问题领域偏置", "用户问题指向专业/职业识别，先形成抽象取象画像，再给最多两个现实落点。"))
        elif domain == "资源/目标/关系" and item["domain"] == "资源/目标/关系":
            item["score"] += 3
            item["evidence"].append(_evidence("question", domain, "问题领域偏置", "用户问题指向资源/关系，优先收敛到资源机会。"))
        if context["age_stage"] == "大学/训练期" and item["domain"] in {"技术/项目/竞赛", "学业/考试/竞赛"}:
            item["score"] += 2
            item["evidence"].append(_evidence("context_frame.age_stage", context["age_stage"], "现代阶段取象", "大学/训练期优先把食伤、官印、财星映射到课程、项目、竞赛、证书、技术实践。"))


def _symbol_sources(payload: dict) -> list[dict]:
    sources = []
    pattern = payload.get("pattern_analysis", {}).get("primary_pattern", {})
    if pattern:
        sources.append({"symbol": pattern.get("name"), "image": "格局取象来源", "evidence": [_evidence("pattern_analysis.primary_pattern", pattern, "格局", f"主格局候选为{pattern.get('name')}。")]})
    flow = (payload.get("analysis_hints") or {}).get("flow_year") or {}
    if flow:
        sources.append({"symbol": flow.get("stem_ten_god"), "image": "流年外显十神", "evidence": [_evidence("analysis_hints.flow_year", flow, "流年", f"流年为{flow.get('ganzhi')}，天干十神{flow.get('stem_ten_god')}。")]})
    return sources


def _secondary_image(candidates: list[dict], main: dict) -> dict:
    for item in candidates:
        if item is not main and item["domain"] != main.get("domain"):
            return item
    return candidates[1] if len(candidates) > 1 else _empty_image()


def _reasoning_chain(payload: dict, main: dict, secondary: dict) -> list[str]:
    chain = []
    if main.get("domain"):
        chain.append(f"主象收敛为{main['domain']}：{main['image']}")
    if secondary.get("domain"):
        chain.append(f"次象保留为{secondary['domain']}：{secondary['image']}")
    chain.append("所有取象必须回指 evidence 字段；没有证据的类象不输出。")
    return chain


def _answer_guidance(payload: dict, domain: str, main: dict, secondary: dict) -> dict:
    if domain != "专业/职业识别":
        return {}
    return {
        "major_or_career_identification": {
            "rule": "专业/职业/行业识别题必须先合参五行旺衰、干支作用、病药喜忌和知识库象义，再归纳现实落点。",
            "max_real_world_landings": 2,
            "knowledge_query_terms": _knowledge_query_terms(payload, main, secondary),
            "knowledge_sources": _knowledge_sources(_knowledge_query_terms(payload, main, secondary)),
            "symbolic_layers": _symbolic_layers(payload),
            "landing_evidence": _landing_evidence(payload),
            "symbolic_dynamics": _symbolic_dynamics(payload),
            "direction_profile": _direction_profile(payload, main, secondary),
            "evidence": _season_strength_evidence(payload),
            "forbidden": "禁止输出五行/十神等于现实专业或行业的直接映射；禁止由工具预设专业名。",
        }
    }


def _knowledge_query_terms(payload: dict, main: dict, secondary: dict) -> list[str]:
    terms = ["五行", "十神", "旺衰", "干支"]
    chart = payload.get("chart") or payload
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    if pattern.get("name"):
        terms.append(pattern["name"])
    for pillar in chart.get("pillars", []):
        terms.append(pillar.get("name", ""))
        if pillar.get("name") == "日柱":
            terms.append("日支")
        stem_ten_god = pillar.get("stem_ten_god")
        if stem_ten_god and stem_ten_god != "日主":
            terms.append(stem_ten_god)
        for hidden in pillar.get("hidden_stems", []):
            ten_god = hidden.get("ten_god")
            if ten_god and ten_god != "日主":
                terms.append(ten_god)
    for relation in chart.get("branch_relationships", []):
        terms.append(f"{relation.get('branches', '')}{relation.get('type', '')}")
    strength = payload.get("strength_analysis") or {}
    forces = strength.get("element_forces") or {}
    for element, item in sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)[:3]:
        terms.append(element)
    if main.get("domain"):
        terms.append(main["domain"])
    if secondary.get("domain"):
        terms.append(secondary["domain"])
    return list(dict.fromkeys(terms))


def _knowledge_sources(terms: list[str]) -> list[dict]:
    sources = []
    for term in terms:
        path = _knowledge_path(term)
        if not path:
            continue
        excerpt = _knowledge_excerpt(path, term)
        if not excerpt:
            continue
        sources.append({
            "term": term,
            "path": str(path),
            "excerpt": excerpt,
        })
        if len(sources) >= 6:
            break
    return sources


def _knowledge_path(term: str) -> Path | None:
    candidates = [
        WIKI_ROOT / "entities" / f"{term}.md",
        WIKI_ROOT / "topics" / f"{term}.md",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _knowledge_excerpt(path: Path, term: str) -> str:
    text = path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content = []
    for line in lines:
        if line.startswith("---") or line.startswith("tags:") or line.startswith("created:") or line.startswith("updated:") or line.startswith("sources:"):
            continue
        content.append(line)
        if len(content) >= 5:
            break
    excerpt = " ".join(content)
    return excerpt[:240] or term


def _symbolic_layers(payload: dict) -> dict:
    data = _load_symbolic_layers()
    dynamics = _symbolic_dynamics(payload)
    query_terms = set(_knowledge_query_terms(payload, {}, {}))
    active_middle = _active_middle_image_names(payload, dynamics)
    return {
        "source_path": str(SYMBOLIC_LAYERS_PATH),
        "traditional_symbols": [
            item for item in data.get("traditional_symbols", [])
            if item.get("name") in query_terms or item.get("kind") in query_terms
        ],
        "middle_images": [
            item for item in data.get("middle_images", [])
            if item.get("name") in active_middle
        ],
        "modern_landing_rules": [
            item for item in data.get("modern_landing_rules", [])
            if set(item.get("requires_all", [])).issubset(active_middle)
        ],
    }


def _landing_evidence(payload: dict) -> dict:
    data = _load_symbolic_layers()
    dynamics = _symbolic_dynamics(payload)
    active_middle = _active_middle_image_names(payload, dynamics)
    middle_strengths = _middle_image_strengths(payload, active_middle)
    result = {"supported": [], "weakened": [], "excluded": []}
    for rule in data.get("modern_landing_rules", []):
        required = set(rule.get("requires_all", []))
        prefers = set(rule.get("prefers_any", []))
        missing = sorted(required - active_middle)
        preferred_hits = sorted(prefers & active_middle)
        evidence = []
        if required:
            evidence.append(f"必要画像：{ '、'.join(rule.get('requires_all', [])) }。")
        if required - set(missing):
            evidence.append(f"已成立画像：{ '、'.join(sorted(required & active_middle)) }。")
        if preferred_hits:
            evidence.append(f"加强画像：{ '、'.join(preferred_hits) }。")
        evidence.extend(_landing_strength_evidence(rule, middle_strengths, active_middle))
        weak_reasons = _landing_rule_weak_reasons(rule, middle_strengths, active_middle)
        if missing:
            evidence.append(f"缺少必要画像：{ '、'.join(missing) }。")
            status = "excluded"
        elif weak_reasons:
            status = "weakened"
            evidence.extend(weak_reasons)
        else:
            status = "supported"
        result[status].append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
            "explanation": rule.get("explanation"),
        })
    return result


def _landing_strength_evidence(rule: dict, middle_strengths: dict[str, dict], active_middle: set[str]) -> list[str]:
    names = list(dict.fromkeys([*rule.get("requires_all", []), *rule.get("prefers_any", [])]))
    evidence = []
    for name in names:
        if name not in active_middle:
            continue
        item = middle_strengths.get(name, {"score": 0, "reasons": []})
        reason_text = "；".join(item.get("reasons", [])) or "由命盘字段合参成立"
        evidence.append(f"{name}画像强弱：{item.get('score')}。{reason_text}。")
    return evidence


def _landing_rule_weak_reasons(rule: dict, middle_strengths: dict[str, dict], active_middle: set[str]) -> list[str]:
    reasons = []
    for name in rule.get("requires_all", []):
        item = middle_strengths.get(name, {"score": 0, "reasons": []})
        if item.get("score", 0) < 1:
            reasons.append(f"{rule['name']}降级：必要画像{name}强度不足，不能作为第一落点。")
    for exclusion in rule.get("excludes_if", []):
        if _exclusion_condition_met(exclusion, middle_strengths, active_middle):
            reasons.append(f"{rule['name']}降级：{exclusion}。")
    return reasons


def _exclusion_condition_met(exclusion: str, middle_strengths: dict[str, dict], active_middle: set[str]) -> bool:
    def score(name: str) -> float:
        return middle_strengths.get(name, {}).get("score", 0)

    if "火弱受制" in exclusion or "火弱" in exclusion:
        return score("规则训练") < 1 or score("工程系统") > score("规则训练")
    if "资源经营无力" in exclusion or "财弱无根" in exclusion:
        return score("资源经营") < 1
    if "文本表达弱于工程系统" in exclusion:
        return score("文本表达") < score("工程系统")
    if "人文研究缺少印星承载" in exclusion:
        return score("人文研究") < 1
    if "制度法理无印承载" in exclusion:
        return score("制度法理") < 1
    if "规则训练弱于技术项目输出" in exclusion:
        return score("规则训练") < score("技能输出")
    if "教育训练缺少印食配合" in exclusion:
        return score("教育训练") < 1
    if "表达输出弱于工程项目训练" in exclusion:
        return score("文本表达") < max(score("工程系统"), score("技能输出"))
    if "公共传播缺少财星外显" in exclusion or "受众连接" in exclusion:
        return score("公共传播") < 1
    if "表达输出被重扰" in exclusion:
        return score("文本表达") < 1
    if "信息处理无力" in exclusion:
        return score("信息处理") < 1
    if "纯资源经营强于技能输出" in exclusion:
        return score("资源经营") > score("技能输出")
    return False


def _middle_image_strengths(payload: dict, active_middle: set[str]) -> dict[str, dict]:
    forces = (payload.get("strength_analysis") or {}).get("element_forces") or {}
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    remedy = payload.get("remedy_analysis") or {}
    context = _context_frame(payload)
    visible_ten_god = ((payload.get("analysis_hints") or {}).get("flow_year") or {}).get("stem_ten_god", "")
    conflicts = "；".join(remedy.get("conflicts", []))
    strengths = {}

    def add(name: str, score: float, reason: str) -> None:
        if name not in active_middle:
            return
        item = strengths.setdefault(name, {"score": 1.0, "reasons": []})
        item["score"] = round(item["score"] + score, 2)
        item["reasons"].append(reason)

    water = forces.get("水", {})
    fire = forces.get("火", {})
    metal = forces.get("金", {})
    earth = forces.get("土", {})
    wood = forces.get("木", {})

    add("信息处理", 0.35 if water.get("effective_power", 0) >= 1 else -0.35, f"水有效力{water.get('effective_power')}、季节系数{water.get('season_power')}")
    add("信息处理", 0.25 if pattern.get("name") in {"食神格", "伤官格"} else 0, f"格局为{pattern.get('name')}，参与理解和输出")
    add("技能输出", 0.45 if pattern.get("name") in {"食神格", "伤官格"} else -0.25, f"格局为{pattern.get('name')}，取作品、项目、训练成果")
    add("技能输出", -0.15 if "劫财" in conflicts else 0, "格局受比劫扰动时，输出仍可用但稳定性下降")
    add("工程系统", 0.45 if metal.get("effective_power", 0) >= 2 else -0.2, f"金有效力{metal.get('effective_power')}，主结构、工具、精密")
    add("工程系统", 0.2 if earth.get("effective_power", 0) >= 1 else 0, f"土有效力{earth.get('effective_power')}，能承载体系")
    add("规则训练", 0.2 if context["age_stage"] == "大学/训练期" else 0, f"现代阶段为{context['age_stage']}")
    add("规则训练", -0.25 if fire.get("season_power", 0) < 0.8 else 0.15, f"火季节系数{fire.get('season_power')}，规则显化受季节影响")
    add("规则训练", -0.2 if fire.get("damage_notes") else 0, f"火受扰：{'、'.join(fire.get('damage_notes', [])) or '无明显冲害'}")
    add("资源经营", 0.35 if "财" in visible_ten_god else -0.2, f"流年外显十神为{visible_ten_god}")
    add("资源经营", 0.25 if wood.get("effective_power", 0) > 0.8 else -0.45, f"木有效力{wood.get('effective_power')}、根气{wood.get('root_status')}")
    add("文本表达", 0.3 if pattern.get("name") in {"食神格", "伤官格"} else -0.2, f"格局为{pattern.get('name')}，带表达和作品象")
    add("文本表达", -0.3 if metal.get("effective_power", 0) >= 2 else 0, f"金有效力{metal.get('effective_power')}，结构/工程画像对纯文本表达形成竞争")
    add("制度法理", 0.3 if metal.get("effective_power", 0) >= 2 else -0.2, f"金有效力{metal.get('effective_power')}，带边界、裁断、规范")
    add("制度法理", -0.2 if fire.get("season_power", 0) < 0.8 or fire.get("damage_notes") else 0.1, f"火季节系数{fire.get('season_power')}，受扰：{'、'.join(fire.get('damage_notes', [])) or '无明显冲害'}")
    add("教育训练", 0.25 if context["age_stage"] == "大学/训练期" else 0, f"现代阶段为{context['age_stage']}，学历训练语境成立")
    add("教育训练", -0.2 if "劫财" in conflicts else 0, "比劫扰格时，知识传递象弱于技能项目输出")
    add("公共传播", 0.25 if "财" in visible_ten_god else -0.2, f"流年外显十神为{visible_ten_god}，决定受众/目标连接")
    add("公共传播", -0.35 if wood.get("effective_power", 0) <= 0.8 or wood.get("root_status") == "无根" else 0.15, f"木有效力{wood.get('effective_power')}、根气{wood.get('root_status')}")
    add("人文研究", 0.25 if water.get("effective_power", 0) >= 1 else -0.2, f"水有效力{water.get('effective_power')}，带阅读、理解、阐释")
    add("人文研究", -0.25 if metal.get("effective_power", 0) >= 2 else 0, f"金有效力{metal.get('effective_power')}，工程系统画像更强")

    for name in active_middle:
        strengths.setdefault(name, {"score": 1.0, "reasons": ["由命盘字段合参成立"]})
    return strengths


def _load_symbolic_layers() -> dict:
    if not SYMBOLIC_LAYERS_PATH.exists():
        return {"traditional_symbols": [], "middle_images": [], "modern_landing_rules": []}
    return json.loads(SYMBOLIC_LAYERS_PATH.read_text(encoding="utf-8"))


def _active_middle_image_names(payload: dict, dynamics: dict) -> set[str]:
    names = set()
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    forces = (payload.get("strength_analysis") or {}).get("element_forces") or {}
    context = _context_frame(payload)
    visible_ten_god = ((payload.get("analysis_hints") or {}).get("flow_year") or {}).get("stem_ten_god", "")

    if forces.get("水", {}).get("effective_power", 0) >= 1 or pattern.get("name") in {"食神格", "伤官格"}:
        names.add("信息处理")
    if pattern.get("name") in {"食神格", "伤官格"}:
        names.add("技能输出")
        names.add("文本表达")
    if forces.get("金", {}).get("effective_power", 0) >= 2 or forces.get("土", {}).get("effective_power", 0) >= 1:
        names.add("工程系统")
    if context["age_stage"] == "大学/训练期" or "官" in visible_ten_god or "印" in visible_ten_god:
        names.add("规则训练")
        names.add("教育训练")
    if forces.get("金", {}).get("effective_power", 0) >= 2 and (context["age_stage"] == "大学/训练期" or "官" in visible_ten_god):
        names.add("制度法理")
    if "财" in visible_ten_god and forces.get("木", {}).get("effective_power", 0) > 0.8:
        names.add("资源经营")
    if "财" in visible_ten_god and pattern.get("name") in {"食神格", "伤官格"}:
        names.add("公共传播")
    if forces.get("水", {}).get("effective_power", 0) >= 1 and context["age_stage"] == "大学/训练期":
        names.add("人文研究")
    return names


def _symbolic_dynamics(payload: dict) -> dict:
    forces = (payload.get("strength_analysis") or {}).get("element_forces") or {}
    strength = payload.get("strength_analysis") or {}
    climate = payload.get("climate_analysis") or {}
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    remedy = payload.get("remedy_analysis") or {}
    hints = payload.get("analysis_hints") or {}
    relations = hints.get("activated_relations") or []

    sorted_forces = sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)
    dominant = [
        f"{element}有效力{item.get('effective_power')}、季节系数{item.get('season_power')}、{item.get('root_status')}"
        for element, item in sorted_forces[:2]
    ]
    usable = [
        f"{item.get('element')}为{item.get('role')}"
        for item in remedy.get("remedy_candidates", [])
        if item.get("element") and item.get("role")
    ]
    weakened = [
        f"{element}有效力{item.get('effective_power')}、季节系数{item.get('season_power')}、{item.get('root_status')}"
        for element, item in sorted_forces
        if item.get("effective_power", 0) <= 0.8 or item.get("root_status") in {"无根", "根受损"}
    ]
    relation_text = [item.get("evidence") for item in relations if item.get("evidence")]
    if pattern.get("name"):
        relation_text.append(f"月令取格为{pattern['name']}，证据为{pattern.get('evidence')}")
    if climate.get("season_profile"):
        relation_text.append(f"调候背景为{climate.get('season_profile')}，寒暖燥湿为{climate.get('temperature')}/{climate.get('moisture')}")

    return {
        "dominant": dominant,
        "usable": usable,
        "weakened": weakened,
        "relations": relation_text,
    }


def _direction_profile(payload: dict, main: dict, secondary: dict) -> dict:
    context = _context_frame(payload)
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    climate = payload.get("climate_analysis") or {}
    remedy = payload.get("remedy_analysis") or {}
    forces = (payload.get("strength_analysis") or {}).get("element_forces") or {}

    favorable = []
    if pattern.get("name") in {"食神格", "伤官格"}:
        favorable.extend(["脑力理解", "表达输出", "技能产出", "项目训练"])
    if context["age_stage"] == "大学/训练期":
        favorable.extend(["课程体系", "证书训练", "技术实践", "实习准备"])
    if "金" in forces and forces["金"].get("effective_power", 0) >= 2:
        favorable.extend(["结构化", "系统化", "工具化", "工程训练"])
    if climate.get("preferred_elements"):
        favorable.append("需要" + "、".join(climate["preferred_elements"]) + "来承载和成事")

    weak = []
    if "木" in forces and forces["木"].get("effective_power", 0) <= 0.8:
        weak.append("纯资源开拓或人脉经营型不宜作为第一落点")
    for conflict in remedy.get("conflicts", [])[:2]:
        weak.append(conflict)

    constraints = [
        "现实专业/行业只能作为抽象画像在当代语境下的归纳，不可写成五行或十神的等号映射。",
        "如果知识库象义与命盘作用关系不能同时支持某个现实落点，应降为待核验或不输出。",
    ]
    if main.get("domain"):
        constraints.append(f"主象领域先收敛为{main['domain']}，再结合知识库象义归纳现实落点。")
    if secondary.get("domain"):
        constraints.append(f"次象领域仅作辅助：{secondary['domain']}。")

    return {
        "favorable_modes": list(dict.fromkeys(favorable)),
        "weak_or_unsuitable_modes": list(dict.fromkeys(weak)),
        "real_world_landing_constraints": constraints,
    }


def _season_strength_evidence(payload: dict) -> list[dict]:
    strength = payload.get("strength_analysis") or {}
    month_branch = strength.get("month_branch")
    forces = strength.get("element_forces") or {}
    evidence = []
    for element, item in sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)[:3]:
        evidence.append(_evidence(
            f"strength_analysis.element_forces.{element}",
            {
                "season_power": item.get("season_power"),
                "effective_power": item.get("effective_power"),
                "root_status": item.get("root_status"),
            },
            "月令季节力量与有效力量",
            f"{month_branch}月下{element}的季节系数为{item.get('season_power')}，有效力量为{item.get('effective_power')}，根气状态为{item.get('root_status')}。",
        ))
    day_strength = strength.get("day_master_strength") or {}
    for text in day_strength.get("evidence", [])[:2]:
        evidence.append(_evidence("strength_analysis.day_master_strength.evidence", text, "日主强弱证据", text))
    return evidence


def _image(domain: str, image: str, score: int, evidence: list[dict]) -> dict:
    return {
        "domain": domain,
        "image": image,
        "score": score,
        "evidence": evidence,
    }


def _empty_image() -> dict:
    return {"domain": None, "image": None, "score": 0, "evidence": []}


def _evidence(source_field: str, source_value, rule: str, text: str) -> dict:
    return {
        "source_field": source_field,
        "source_value": source_value,
        "rule": rule,
        "text": text,
    }
