from __future__ import annotations


QUESTION_TEMPLATES = {
    "事业/工作": {
        "template_id": "career_work",
        "main_images": [
            {"six_relative": "官鬼", "image": "职位/岗位/规则/上级", "reason": "求职、工作、offer 以官鬼为职位和规则主象。"},
        ],
        "auxiliary_images": [
            {"six_relative": "父母", "image": "合同/通知/单位文书", "reason": "入职、offer、合同、通知等流程载体取父母。"},
            {"six_relative": "妻财", "image": "薪资/收益/现实利益", "reason": "薪资待遇和现实收益取妻财。"},
            {"six_relative": "兄弟", "image": "竞争者/同事/消耗", "reason": "竞争、同事、分利和阻力可看兄弟。"},
        ],
        "conflict_rules": [
            "工作 + 合同：官鬼为岗位主轴，父母为文书流程辅助轴。",
            "工作 + 薪资：官鬼为岗位主轴，妻财为薪资收益辅助轴。",
            "工作 + 竞争：官鬼为岗位主轴，兄弟为竞争阻力辅助轴。",
        ],
    },
    "财运/交易": {
        "template_id": "wealth_trade",
        "main_images": [
            {"six_relative": "妻财", "image": "钱财/货物/收入/客户资源", "reason": "求财、交易、收款以妻财为财物主象。"},
        ],
        "auxiliary_images": [
            {"six_relative": "子孙", "image": "客源/产出/解决方案", "reason": "生财之路、产品产出、客户流量可取子孙。"},
            {"six_relative": "兄弟", "image": "竞争/分财/成本消耗", "reason": "分财、竞争、成本消耗可取兄弟。"},
            {"six_relative": "父母", "image": "合同/票据/手续", "reason": "交易合同、票据、手续取父母。"},
        ],
        "conflict_rules": [
            "钱财 + 合同：妻财为财物主轴，父母为手续辅助轴。",
            "钱财 + 竞争：妻财为财物主轴，兄弟为分财阻力。",
            "钱财 + 客户：妻财为收益主轴，子孙为客源或产出辅助轴。",
        ],
    },
    "感情/婚恋": {
        "template_id": "relationship",
        "main_images": [
            {"six_relative": "妻财", "image": "女方/妻子/现实吸引", "reason": "男问感情多以妻财为对象主象。"},
            {"six_relative": "官鬼", "image": "男方/丈夫/关系约束", "reason": "女问感情多以官鬼为对象主象。"},
        ],
        "auxiliary_images": [
            {"six_relative": "世应", "image": "双方关系", "reason": "关系互动必须合看世应。"},
            {"six_relative": "兄弟", "image": "竞争者/朋友干扰", "reason": "竞争者、同辈干扰、分夺可看兄弟。"},
            {"six_relative": "父母", "image": "婚书/家长/现实条件", "reason": "婚书、家长、房屋、现实制度条件可看父母。"},
        ],
        "conflict_rules": [
            "感情对象不明时，不强行按性别定单一用神；保留世应互动和对象六亲两层。",
            "对象 + 家长/婚书：对象六亲为主轴，父母为现实条件辅助轴。",
        ],
    },
    "考试/学业": {
        "template_id": "exam_study",
        "main_images": [
            {"six_relative": "父母", "image": "试卷/证书/录取文书/学习材料", "reason": "考试、证书、录取、申请材料以父母为主象。"},
        ],
        "auxiliary_images": [
            {"six_relative": "官鬼", "image": "排名/规则/压力/录取约束", "reason": "考试规则、压力、名次和录取约束可看官鬼。"},
            {"six_relative": "子孙", "image": "发挥/表达/解题输出", "reason": "考试发挥、表达输出、解题思路可看子孙。"},
        ],
        "conflict_rules": [
            "考试 + 证书：父母为文书主轴。",
            "考试 + 发挥：父母为考试载体主轴，子孙为发挥辅助轴。",
            "考试 + 压力/规则：父母为文书主轴，官鬼为规则压力辅助轴。",
        ],
    },
    "健康/疾病": {
        "template_id": "health_illness",
        "main_images": [
            {"six_relative": "官鬼", "image": "疾病/病因/压力源", "reason": "疾病、病症、压力源以官鬼为病象主轴。"},
        ],
        "auxiliary_images": [
            {"six_relative": "子孙", "image": "药物/治疗方案/恢复力", "reason": "药物、治疗、缓解和恢复方案取子孙。"},
            {"six_relative": "父母", "image": "医院/检查报告/病历", "reason": "医院、检查报告、病历文书取父母。"},
        ],
        "conflict_rules": [
            "疾病 + 治疗：官鬼为病象主轴，子孙为药物治疗辅助轴。",
            "疾病 + 报告：官鬼为病象主轴，父母为检查文书辅助轴。",
        ],
    },
    "失物/寻找": {
        "template_id": "lost_found",
        "main_images": [
            {"six_relative": "妻财", "image": "财物/普通物品", "reason": "普通财物、贵重物品多以妻财为主象。"},
            {"six_relative": "父母", "image": "证件/文书/衣物/房屋内物件", "reason": "证件、文书、衣物、资料类物品可取父母。"},
            {"six_relative": "子孙", "image": "小物件/玩具/子女相关物", "reason": "玩具、小物件、子女相关物可取子孙。"},
        ],
        "auxiliary_images": [
            {"six_relative": "世应", "image": "自己与外部位置", "reason": "失物需合看世应代表内外、自他和找寻关系。"},
        ],
        "conflict_rules": [
            "失物物类不明时，不能强行定单一用神；保留物类候选。",
            "证件类优先父母，钱财类优先妻财，玩具小物类可取子孙。",
        ],
    },
    "诉讼/纠纷": {
        "template_id": "dispute_lawsuit",
        "main_images": [
            {"six_relative": "官鬼", "image": "官非/规则/压力/处罚", "reason": "诉讼、纠纷、处罚和规则压力以官鬼为主象。"},
        ],
        "auxiliary_images": [
            {"six_relative": "父母", "image": "文书/证据/判书/合同", "reason": "证据、合同、文书、判书取父母。"},
            {"six_relative": "兄弟", "image": "对立方/竞争方/牵连者", "reason": "对立竞争、牵连、同辈争夺可看兄弟。"},
            {"six_relative": "妻财", "image": "赔偿/钱财争议", "reason": "赔偿、罚款、财产争议取妻财。"},
        ],
        "conflict_rules": [
            "纠纷 + 合同证据：官鬼为压力规则主轴，父母为证据文书辅助轴。",
            "纠纷 + 赔偿：官鬼为规则主轴，妻财为赔偿财物辅助轴。",
        ],
    },
}

MUST_NOT_MIX = [
    "模板只决定取象入口，不决定最终成败。",
    "模板不能覆盖 useful_god_selection 的分层结果。",
    "模板只能做领域翻译，不能用行业先验覆盖卦内证据。",
    "模板不能引入八字或大六壬逻辑。",
]

REAL_IMAGE_RULES = [
    "先抓实象：先列用神、世应、月日、旬空、动变、飞伏、三合、进退、应期候选和神煞等 JSON 已给出的硬证据。",
    "实象优先于领域联想：领域语境只能翻译六亲和爻象，不得替代用神链、月日、世应、动变与 completion_chain。",
    "冲突也是实象：有利证据和阻断证据同时存在时，保留先后、内外、显隐和强弱差异，不强压成单一结论。",
]

TIME_LAYER_RULES = [
    {
        "layer": "already_formed",
        "name": "已然",
        "evidence": "月建、静卦格局、用神持世/临应、上卦且有力的主象。",
        "instruction": "月建可表示占前或当月已经形成的背景；静卦优先说明既成格局，不直接推出未来剧烈变化。",
    },
    {
        "layer": "current_trigger",
        "name": "当前",
        "evidence": "日辰、日冲日合、日生克、旬空压力、世应当前关系。",
        "instruction": "日辰可表示眼前触发或近事变化，用于判断当前损益、压力、兑现或冲突。",
    },
    {
        "layer": "future_development",
        "name": "未然",
        "evidence": "动爻、变爻、回头生克、伏神出伏、三合补缺、进退神、timing_analysis.candidates。",
        "instruction": "未来只从动变、飞伏、补缺、进退和应期候选推出；不得脱离 JSON 自行造应期。",
    },
]

ALREADY_FUTURE_SPLIT = {
    "already_formed": "说明卦中已经存在、已经发生或占前形成的部分。",
    "current_trigger": "说明眼前正在触发的得失、压力、兑现、回撤或冲突。",
    "future_development": "说明后续可能被引动、填实、冲开、推进或转化的部分。",
    "reversal_patterns": [
        "先有利后受损",
        "先受阻后转通",
        "账面有而未兑现",
        "旺而被制",
        "弱而得救",
        "显处有利而暗处受伤",
    ],
}

DOMAIN_TRANSLATION_RULES = [
    "领域只翻译六亲象和爻象的语言，不改变六亲、用神、原忌仇闲神和月日动变关系。",
    "同一六亲在不同问题中可有不同表述，但必须来自 question_template 的主象、辅助象或 JSON 已给字段。",
    "不得用行业先验覆盖卦内证据；如果领域联想与实象冲突，优先保留实象并标记不确定。",
]


def build_question_template(domain: str, question: str | None = None) -> dict:
    template = QUESTION_TEMPLATES.get(domain)
    selected_by = ["question_context.domain"]
    if question:
        selected_by.append("question_tokens")
    if template is None:
        return {
            "template_id": "uncategorized",
            "domain": domain,
            "selected_by": selected_by,
            "main_images": [],
            "auxiliary_images": [],
            "conflict_rules": [],
            "secondary_templates": [],
            "real_image_rules": REAL_IMAGE_RULES,
            "time_layer_rules": TIME_LAYER_RULES,
            "already_future_split": ALREADY_FUTURE_SPLIT,
            "domain_translation_rules": DOMAIN_TRANSLATION_RULES,
            "must_not_mix": MUST_NOT_MIX,
        }
    return {
        "template_id": template["template_id"],
        "domain": domain,
        "selected_by": selected_by,
        "main_images": list(template["main_images"]),
        "auxiliary_images": list(template["auxiliary_images"]),
        "conflict_rules": list(template["conflict_rules"]),
        "secondary_templates": [],
        "real_image_rules": REAL_IMAGE_RULES,
        "time_layer_rules": TIME_LAYER_RULES,
        "already_future_split": ALREADY_FUTURE_SPLIT,
        "domain_translation_rules": DOMAIN_TRANSLATION_RULES,
        "must_not_mix": MUST_NOT_MIX,
    }
