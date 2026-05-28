from __future__ import annotations

from typing import Any


MIDDLE_IMAGES = {
    "信息处理",
    "技能输出",
    "工程系统",
    "文本表达",
    "制度法理",
    "规则训练",
    "人文研究",
    "公共传播",
    "教育训练",
    "资源经营",
    "艺术设计",
    "生命健康",
    "研究专精",
    "跨域迁移",
}

QUESTION_KEYWORDS = {
    "信息处理": ("信息", "数据", "软件", "计算机", "智能", "模型"),
    "技能输出": ("技术", "项目", "作品", "实践", "技能"),
    "工程系统": ("工程", "系统", "硬件", "制造", "建筑"),
    "文本表达": ("中文", "文学", "写作", "语言", "表达"),
    "制度法理": ("法律", "法学", "公务", "政策", "治理"),
    "规则训练": ("规则", "规范", "训练", "纪律"),
    "人文研究": ("历史", "哲学", "文化", "研究"),
    "公共传播": ("传播", "媒体", "新闻", "平台", "内容"),
    "教育训练": ("教育", "师范", "培训", "课程"),
    "资源经营": ("商业", "管理", "金融", "经营", "市场"),
    "艺术设计": ("艺术", "设计", "审美", "创意"),
    "生命健康": ("医学", "健康", "心理", "生命", "护理"),
    "研究专精": ("研究", "学术", "理论", "深造"),
    "跨域迁移": ("跨", "复合", "交叉", "转专业"),
}

DISCIPLINE_GROUPS = {
    "humanities_text": {"文本表达": 1.0, "人文研究": 0.9, "研究专精": 0.45, "教育训练": 0.25},
    "law_public_policy": {"制度法理": 1.0, "规则训练": 0.55, "公共传播": 0.35, "资源经营": 0.3, "信息处理": 0.25},
    "stem_engineering": {"工程系统": 1.0, "技能输出": 0.75, "信息处理": 0.45, "研究专精": 0.3, "规则训练": 0.2},
    "information_data": {"信息处理": 1.0, "工程系统": 0.45, "技能输出": 0.35, "研究专精": 0.25},
    "business_management": {"资源经营": 1.0, "制度法理": 0.35, "公共传播": 0.3, "信息处理": 0.3},
    "media_communication": {"公共传播": 1.0, "文本表达": 0.4, "艺术设计": 0.35, "跨域迁移": 0.3},
    "education_training": {"教育训练": 1.0, "规则训练": 0.45, "文本表达": 0.35, "研究专精": 0.3, "信息处理": 0.2},
    "arts_design": {"艺术设计": 1.0, "公共传播": 0.4, "技能输出": 0.3, "文本表达": 0.25},
    "health_life_science": {"生命健康": 1.0, "研究专精": 0.4, "教育训练": 0.3, "规则训练": 0.25, "制度法理": 0.2},
}

CROSS_DOMAIN_PAIRS = {
    frozenset(("information_data", "media_communication")),
    frozenset(("education_training", "information_data")),
    frozenset(("law_public_policy", "information_data")),
    frozenset(("business_management", "information_data")),
    frozenset(("arts_design", "stem_engineering")),
    frozenset(("health_life_science", "education_training")),
    frozenset(("health_life_science", "humanities_text")),
}

CONSTRAINTS_FOR_LLM = [
    "不得强行归为纯文或纯理",
    "只能从高分族群组合联想到现代专业/职业",
    "最多输出两个现实落点",
    "联网检索只能用于解释现代专业实际学习内容，不得覆盖命盘画像裁决",
    "不得由单一神煞、五行或十神直接定专业",
]


def build_middle_image_scores(
    base_scores: dict[str, dict[str, Any]],
    spirit_sha_analysis: dict[str, Any],
    question: str = "",
) -> dict[str, dict[str, Any]]:
    scores = {
        image: {
            "base_score": _base_score(item or {}),
            "spirit_delta": 0.0,
            "question_delta": 0.0,
            "final_score": 0.0,
            "evidence": list((item or {}).get("evidence") or []),
        }
        for image, item in base_scores.items()
        if image in MIDDLE_IMAGES
    }

    for image in MIDDLE_IMAGES:
        if image not in scores:
            scores[image] = {
                "base_score": 0.0,
                "spirit_delta": 0.0,
                "question_delta": 0.0,
                "final_score": 0.0,
                "evidence": [],
            }

    _apply_spirit_deltas(scores, spirit_sha_analysis)
    _apply_question_deltas(scores, question)

    return {
        image: {
            **item,
            "spirit_delta": round(item["spirit_delta"], 3),
            "question_delta": round(item["question_delta"], 3),
            "final_score": round(item["base_score"] + item["spirit_delta"] + item["question_delta"], 3),
        }
        for image, item in scores.items()
        if item["base_score"] or item["spirit_delta"] or item["question_delta"] or item["evidence"]
    }


def build_discipline_profile(
    middle_image_scores: dict[str, dict[str, Any]],
    question: str = "",
) -> dict[str, Any]:
    groups = [_score_group(name, weights, middle_image_scores) for name, weights in DISCIPLINE_GROUPS.items()]
    groups = [group for group in groups if group["score"] > 0]
    groups.sort(key=lambda item: (-item["score"], item["name"]))
    cross_domain = _is_cross_domain(groups)
    return {
        "groups": groups,
        "cross_domain": cross_domain,
        "recommended_mode": _recommended_mode(groups, cross_domain, question),
        "constraints_for_llm": list(CONSTRAINTS_FOR_LLM),
    }


def _apply_spirit_deltas(scores: dict[str, dict[str, Any]], spirit_sha_analysis: dict[str, Any]) -> None:
    per_image_totals = {image: 0.0 for image in scores}
    for hit in (spirit_sha_analysis or {}).get("active") or []:
        supports = [image for image in hit.get("supports", []) if image in scores]
        if not supports:
            continue
        hit_delta = min(_number(hit.get("score_delta", 0.08)), 0.2)
        for image in supports:
            remaining = 0.35 - per_image_totals[image]
            if remaining <= 0:
                continue
            delta = min(hit_delta, remaining)
            if scores[image]["base_score"] <= 0:
                delta = min(delta, 0.08)
            if delta <= 0:
                continue
            scores[image]["spirit_delta"] += delta
            per_image_totals[image] += delta
            scores[image]["evidence"].append(_spirit_evidence(hit, image, delta))


def _apply_question_deltas(scores: dict[str, dict[str, Any]], question: str) -> None:
    if not question:
        return
    for image, keywords in QUESTION_KEYWORDS.items():
        if image in scores and _has_chart_or_spirit_evidence(scores[image]) and any(keyword in question for keyword in keywords):
            scores[image]["question_delta"] += 0.1
            scores[image]["evidence"].append(f"问题语境指向{image}。")
    if any(keyword in question for keyword in ("专业", "职业", "学什么", "高考", "就业")):
        for image in ("信息处理", "技能输出", "制度法理", "教育训练", "公共传播"):
            if not _has_chart_or_spirit_evidence(scores[image]):
                continue
            scores[image]["question_delta"] += 0.05
            scores[image]["evidence"].append("专业/职业问题语境下保留该中间画像。")


def _score_group(name: str, weights: dict[str, float], middle_scores: dict[str, dict[str, Any]]) -> dict[str, Any]:
    supporting_images = []
    spirit_factors = []
    structural_evidence = []
    has_structural_support = False
    score = 0.0
    for image, weight in weights.items():
        item = middle_scores.get(image) or {}
        image_score = _number(item.get("final_score"))
        if image_score <= 0:
            continue
        score += image_score * weight
        supporting_images.append(image)
        if _number(item.get("base_score")) > 0:
            has_structural_support = True
            structural_evidence.extend(item.get("evidence") or [])
        if _number(item.get("spirit_delta")) > 0:
            spirit_factors.append(f"{image}受神煞辅助加权 {round(_number(item.get('spirit_delta')), 3)}")
    if not has_structural_support:
        supporting_images = []
        spirit_factors = []
        structural_evidence = []
        score = 0.0
    score = round(score, 3)
    return {
        "name": name,
        "score": score,
        "supporting_images": supporting_images,
        "spirit_factors": spirit_factors,
        "structural_evidence": structural_evidence,
        "weakening_factors": [] if supporting_images else ["缺少对应中间画像支撑"],
        "confidence": _confidence(score, supporting_images),
    }


def _is_cross_domain(groups: list[dict[str, Any]]) -> bool:
    active = [group for group in groups if group["score"] > 0]
    if len(active) < 2:
        return False
    top, second = active[0], active[1]
    if top["score"] <= 0:
        return False
    close_threshold = max(0.25, top["score"] * 0.2)
    if top["score"] - second["score"] <= close_threshold:
        return True
    for left_index, left in enumerate(active[:4]):
        for right in active[left_index + 1:4]:
            if frozenset((left["name"], right["name"])) in CROSS_DOMAIN_PAIRS:
                pair_threshold = max(0.35, max(left["score"], right["score"]) * 0.25)
                if abs(left["score"] - right["score"]) <= pair_threshold:
                    return True
    return False


def _recommended_mode(groups: list[dict[str, Any]], cross_domain: bool, question: str) -> str:
    active = [group["name"] for group in groups if group["score"] > 0]
    if not active:
        return "证据不足，先保留不确定性并询问现实反馈"
    if cross_domain and len(active) >= 2:
        return f"{active[0]} + {active[1]} 的交叉型方向"
    return f"{active[0]} 主导方向"


def _confidence(score: float, supporting_images: list[str]) -> str:
    if score >= 2.5 and len(supporting_images) >= 2:
        return "high"
    if score >= 1.0:
        return "medium"
    if score > 0:
        return "low"
    return "none"


def _has_chart_or_spirit_evidence(item: dict[str, Any]) -> bool:
    return _number(item.get("base_score")) > 0 or _number(item.get("spirit_delta")) > 0


def _spirit_evidence(hit: dict[str, Any], image: str, delta: float) -> str:
    name = hit.get("name", "神煞")
    strength = hit.get("strength") or "未列强度"
    basis = hit.get("basis", hit.get("value", "未列依据"))
    positions = "、".join(hit.get("hit_positions") or [])
    avoid = hit.get("avoid") or "不得由单一神煞直接定专业"
    return (
        f"{name}辅助{image}，强度{strength}，依据{basis}，"
        f"命中{positions or '未列位置'}，加权{round(delta, 3)}；提示：{avoid}。"
    )


def _base_score(item: dict[str, Any]) -> float:
    for key in ("base_score", "score", "final_score"):
        if key in item:
            return _number(item.get(key))
    return 0.0


def _number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0
