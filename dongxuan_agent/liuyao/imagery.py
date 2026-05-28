from __future__ import annotations


SIX_RELATIVE_IMAGERY = {
    "官鬼": {
        "near_self": ["压力", "忧虑", "约束", "责任", "风险"],
        "far_symbol": ["职位", "规则", "上级", "疾病", "官非", "丈夫/男方"],
        "domains": ["事业/工作", "健康/疾病", "感情/婚恋", "诉讼/纠纷"],
    },
    "父母": {
        "near_self": ["保护", "承载", "学习负担", "信息接收"],
        "far_symbol": ["文书", "合同", "证书", "房屋", "单位", "长辈", "消息"],
        "domains": ["文书/合同", "考试/学业", "事业/工作", "家宅/房屋"],
    },
    "妻财": {
        "near_self": ["资源", "欲望", "收益目标", "现实利益"],
        "far_symbol": ["钱财", "货物", "客户资源", "女方/妻子", "收入"],
        "domains": ["财运/交易", "感情/婚恋", "事业/工作"],
    },
    "子孙": {
        "near_self": ["放松", "产出", "解决方案", "表达", "享乐"],
        "far_symbol": ["药物", "治疗方案", "作品", "客户流量", "子女", "下属"],
        "domains": ["健康/疾病", "财运/交易", "考试/学业", "创作/产出"],
    },
    "兄弟": {
        "near_self": ["同辈", "自我消耗", "竞争心", "分担"],
        "far_symbol": ["竞争者", "合伙人", "同事", "分财者", "阻力"],
        "domains": ["财运/交易", "事业/工作", "合作/竞争"],
    },
}

KEYWORD_IMAGES = {
    "工作": ("官鬼", "far_symbol", "职位"),
    "事业": ("官鬼", "far_symbol", "职位"),
    "职位": ("官鬼", "far_symbol", "职位"),
    "offer": ("官鬼", "far_symbol", "职位"),
    "录用": ("官鬼", "far_symbol", "职位"),
    "合同": ("父母", "far_symbol", "合同"),
    "通知": ("父母", "far_symbol", "消息"),
    "文书": ("父母", "far_symbol", "文书"),
    "证书": ("父母", "far_symbol", "证书"),
    "钱": ("妻财", "far_symbol", "钱财"),
    "财": ("妻财", "far_symbol", "钱财"),
    "收入": ("妻财", "far_symbol", "收入"),
    "药": ("子孙", "far_symbol", "药物"),
    "治疗": ("子孙", "far_symbol", "治疗方案"),
    "客户": ("子孙", "far_symbol", "客户流量"),
    "竞争": ("兄弟", "far_symbol", "竞争者"),
    "同事": ("兄弟", "far_symbol", "同事"),
}


def question_tokens(question: str | None) -> list[str]:
    text = question or ""
    tokens = []
    for keyword in KEYWORD_IMAGES:
        if keyword in text:
            tokens.append(keyword)
    return tokens


def build_imagery_context(question: str | None, domain: str) -> dict:
    tokens = question_tokens(question)
    matches = []
    for token in tokens:
        relative, layer, image = KEYWORD_IMAGES[token]
        matches.append(
            {
                "token": token,
                "six_relative": relative,
                "layer": layer,
                "image": image,
                "reason": f"{token}与{relative}取象中的{image}相符",
            }
        )
    return {
        "question": question,
        "tokens": tokens,
        "domain": domain,
        "matches": matches,
        "near_self_principle": "近取诸身：先看世爻、持世六亲、作用到世爻的候选。",
        "far_symbol_principle": "远取诸象：外部对象、文书、职位、钱财、对方等按六亲取象分层。",
    }


def build_useful_god_selection(
    payload: dict,
    derived_lines: list[dict],
    useful_god_analysis: dict,
    imagery_context: dict,
) -> dict:
    shi = next(line for line in derived_lines if line["is_shi"])
    near_self_focus = [
        {
            "position": shi["position"],
            "name": shi["name"],
            "six_relative": shi["six_relative"],
            "role": shi["role"],
            "reason": "世爻代表求测人自身与承接能力",
            "strength": shi["effective_strength"],
            "cautions": _line_cautions(shi),
        }
    ]
    far_symbol_focus = _far_symbol_focus(useful_god_analysis, imagery_context)
    conflicts = _conflicts(far_symbol_focus)
    relatives = [item["six_relative"] for item in far_symbol_focus]
    main = _main_useful_god(relatives, useful_god_analysis)
    auxiliaries = [relative for relative in relatives if relative != main]
    status = _selection_status(main, auxiliaries, useful_god_analysis)
    return {
        "principle": "近取诸身，远取诸象",
        "mode": "imagery_guided",
        "near_self_focus": near_self_focus,
        "far_symbol_focus": far_symbol_focus,
        "conflicts": conflicts,
        "primary_axis": _primary_axis(main),
        "secondary_axes": _secondary_axes(auxiliaries),
        "selection_result": {
            "status": status,
            "main_useful_god": main,
            "auxiliary_useful_gods": auxiliaries,
            "watch_relatives": ["兄弟"] if any(line["six_relative"] == "兄弟" for line in derived_lines) else [],
            "conflict_reading": _conflict_reading(main, auxiliaries),
        },
    }


def _line_cautions(line: dict) -> list[str]:
    cautions = []
    if line["void_state"]["is_void"]:
        cautions.append("旬空")
    if line["extreme_state"] != "none":
        cautions.append(line["extreme_state"])
    return cautions


def _far_symbol_focus(useful_god_analysis: dict, imagery_context: dict) -> list[dict]:
    by_relative = {candidate["six_relative"]: candidate for candidate in useful_god_analysis["candidates"]}
    result = []
    seen = set()
    for match in imagery_context["matches"]:
        relative = match["six_relative"]
        if relative in seen or relative not in by_relative:
            continue
        candidate = by_relative[relative]
        result.append(
            {
                "six_relative": relative,
                "image": match["image"],
                "matching_lines": [line["position"] for line in candidate["matching_lines"]],
                "reason": f"{match['token']}以{relative}之{match['image']}为象",
            }
        )
        seen.add(relative)
    return result


def _conflicts(far_symbol_focus: list[dict]) -> list[dict]:
    if len(far_symbol_focus) < 2:
        return []
    relatives = [item["six_relative"] for item in far_symbol_focus]
    return [
        {
            "type": "layered_imagery",
            "summary": "同一问题包含多个有效取象层",
            "candidates": relatives,
            "near_self_question": "世爻能否承接此事及其压力",
            "far_symbol_question": "外部对象、流程或载体是否同步成事",
            "interpretation_hint": _interpretation_hint(relatives),
        }
    ]


def _interpretation_hint(relatives: list[str]) -> str:
    if {"官鬼", "父母"} <= set(relatives):
        return "官鬼与父母不是互斥；前者看岗位/规则，后者看文书/通知。"
    return "多个取象不是互斥；应按近身与远象分层解读。"


def _main_useful_god(relatives: list[str], useful_god_analysis: dict) -> str | None:
    if not relatives:
        first = useful_god_analysis["candidates"][0] if useful_god_analysis["candidates"] else None
        return first["six_relative"] if first and first["matching_lines"] else None
    domain = useful_god_analysis["domain"]
    if domain == "事业/工作" and "官鬼" in relatives:
        return "官鬼"
    return relatives[0]


def _selection_status(main: str | None, auxiliaries: list[str], useful_god_analysis: dict) -> str:
    if main is None:
        return "missing" if useful_god_analysis["missing_candidates"] else "ambiguous"
    if auxiliaries:
        return "layered"
    return "selected"


def _primary_axis(main: str | None) -> list[dict]:
    if main is None:
        return []
    return [
        {
            "axis": "self_to_main_symbol",
            "near": "世爻",
            "far": main,
            "reason": "近取世爻承接，远取主象判断外部事项。",
        }
    ]


def _secondary_axes(auxiliaries: list[str]) -> list[dict]:
    return [
        {
            "axis": f"self_to_{relative}",
            "near": "世爻",
            "far": relative,
            "reason": "辅助象用于解释流程、载体或旁证。",
        }
        for relative in auxiliaries
    ]


def _conflict_reading(main: str | None, auxiliaries: list[str]) -> list[str]:
    if main == "官鬼" and "父母" in auxiliaries:
        return [
            "官鬼与父母不是互斥；前者看岗位机会，后者看文书流程。",
            "若官鬼有力而父母受克，可读为岗位有机会但手续/通知受阻。",
        ]
    if auxiliaries:
        return ["多重取象应分层解读，不强行合并为单一用神。"]
    return []
