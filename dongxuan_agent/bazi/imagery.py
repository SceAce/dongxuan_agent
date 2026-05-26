from __future__ import annotations

from datetime import datetime


QUESTION_KEYWORDS = {
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
        "avoid_images": [
            "不能仅凭财星直接断恋爱或得财，必须结合日支、问题背景和岁运引动。",
            "不能仅凭官杀直接断灾祸或上岸，必须结合格局、药病和现实目标。",
            "取象 V1 只做现代语境映射和证据收敛，不替代用户现实反馈。",
        ],
        "reasoning_chain": _reasoning_chain(payload, main, secondary),
        "uncertainty": [
            "取象 V1 使用内置现代类象表，并要求每条象都有 JSON 字段证据；未连接外部时代资料库。",
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
