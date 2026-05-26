from __future__ import annotations


GENERAL_CARDS = (
    {
        "name": "原局结构优先",
        "meaning": "先看原局四柱、日主、月令、十神、藏干、地支关系，再看大运流年引动。",
        "use_when": ["所有八字分析"],
        "avoid": "不可只凭单个流年干支或单个十神直接断具体事件。",
        "sources": ["八字规则 V1：由本地八字资料与项目排盘字段整理"],
        "implemented": True,
    },
    {
        "name": "流年引动",
        "meaning": "流年通过天干十神、地支冲合刑害、伏吟并临来引动原局宫位和十神。",
        "use_when": ["用户询问某一年发生什么", "用户询问某年趋势"],
        "avoid": "流年只说明触发点，不等于事件已经发生；必须合大运和原局。",
        "sources": ["八字规则 V1：大运流年合参"],
        "implemented": True,
    },
    {
        "name": "大运流年合参",
        "meaning": "大运提供十年背景，流年提供当年触发；流年落在大运主题内时事件更明显。",
        "use_when": ["所有带 target_year 的分析"],
        "avoid": "不可脱离大运只看流年，也不可脱离原局只看大运。",
        "sources": ["八字规则 V1：运年命三层合参"],
        "implemented": True,
    },
)


DOMAIN_CARDS = {
    "学业": {
        "name": "学业/考试取象",
        "meaning": "学业考试重点看印、食伤、官杀、月柱和文书规则压力。",
        "use_when": ["问题包含学业、考试、证书、申请、竞赛"],
        "avoid": "印星或官星出现不等于必过，须看冲合刑害和大运流年是否同向。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
    "感情": {
        "name": "感情/关系取象",
        "meaning": "男命以财星为重要关系象，女命以官杀为重要关系象，同时看日支夫妻宫。",
        "use_when": ["问题包含感情、恋爱、对象、关系、婚姻"],
        "avoid": "财星或官杀被引动不能直接断恋爱或结婚，必须合日支和现实背景。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
    "财": {
        "name": "财务/资源取象",
        "meaning": "财务资源看财星、比劫、食伤生财、财被冲合和财星是否透出。",
        "use_when": ["问题包含财、钱、资源、收入、投资"],
        "avoid": "财星出现不等于得财，比劫旺或冲破时可能是消耗竞争。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
}


QUESTION_KEYWORDS = {
    "学业": ("学业", "考试", "证书", "申请", "竞赛", "成绩", "录取", "升学"),
    "感情": ("感情", "恋爱", "对象", "关系", "婚姻", "婚恋", "复合", "桃花"),
    "财": ("财", "钱", "资源", "收入", "投资", "财务", "生意", "资产"),
}


def build_bazi_rule_context(question: str | None = None, target_year: int | None = None) -> dict:
    question = question or ""
    cards = list(GENERAL_CARDS)
    selected_domains = [
        domain
        for domain, keywords in QUESTION_KEYWORDS.items()
        if any(keyword in question for keyword in keywords)
    ]

    if target_year is not None and "学业" not in selected_domains:
        selected_domains.append("学业")
    if target_year is not None and "财" not in selected_domains:
        selected_domains.append("财")

    cards.extend(DOMAIN_CARDS[domain] for domain in selected_domains)

    return {
        "mode": "year_event" if target_year is not None else "chart_structure",
        "target_year": target_year,
        "selection_rule": "规则卡片只提供取象边界；最终结论必须回指 analysis_hints 与命盘字段。",
        "cards": cards,
    }
