from __future__ import annotations


DOMAIN_RULES = (
    ("事业/工作", ("工作", "事业", "职位", "升职", "面试", "单位", "老板"), ("官鬼", "父母")),
    ("财运/交易", ("财", "钱", "收入", "交易", "投资", "生意", "买卖"), ("妻财", "子孙")),
    ("感情/婚恋", ("感情", "恋爱", "婚", "对象", "复合", "伴侣"), ("妻财", "官鬼", "世应")),
    ("考试/学业", ("考试", "学业", "学习", "专业", "证书", "录取"), ("父母", "官鬼")),
    ("健康/疾病", ("健康", "疾病", "病", "身体", "手术"), ("官鬼", "子孙")),
    ("文书/合同", ("合同", "文书", "协议", "证件", "材料"), ("父母", "官鬼")),
)

USEFUL_GOD_REASONS = {
    "官鬼": "事业、职位、规则压力、疾病和约束多以官鬼为候选用神。",
    "父母": "合同、文书、单位、证书、学业资料可取父母为候选用神。",
    "妻财": "钱财、交易、资源收益及男性感情对象可取妻财为候选用神。",
    "子孙": "产出、缓解、医药效果、客户流量和财源可取子孙为候选用神。",
    "世应": "感情与合作类问题需重点看世应关系，世应不是六亲但必须纳入裁决。",
}


def classify_question(question: str | None) -> dict:
    text = question or ""
    for domain, keywords, candidates in DOMAIN_RULES:
        if any(keyword in text for keyword in keywords):
            return _context(domain, candidates)
    return _context("综合/未分类", ("世应",))


def _context(domain: str, candidates: tuple[str, ...]) -> dict:
    return {
        "domain": domain,
        "candidate_useful_gods": [
            {
                "six_relative": candidate,
                "reason": USEFUL_GOD_REASONS[candidate],
            }
            for candidate in candidates
        ],
        "avoid": [
            "候选用神不等于最终用神，必须结合世应、动爻、月日旺衰和生克关系。",
        ],
    }
