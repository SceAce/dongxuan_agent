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
