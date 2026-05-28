# Bazi Cross-Discipline Imagery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-backed Bazi spirit-sha assistance and multi-dimensional discipline profiling for major/career imagery without forcing humanities/STEM binaries.

**Architecture:** Keep `build_imagery_analysis()` as the public entry point, but move new responsibilities into focused modules. `dongxuan_agent/bazi/spirits.py` calculates Bazi-specific spirit-sha hits from existing payload fields. `dongxuan_agent/bazi/discipline.py` builds middle-image scores and discipline group profiles, then `dongxuan_agent/bazi/imagery.py` attaches those outputs under `answer_guidance.major_or_career_identification`.

**Tech Stack:** Python 3, pytest, existing `dongxuan_agent.bazi` modules, no new third-party dependencies.

---

## File Structure

- Create `dongxuan_agent/bazi/spirits.py`: Bazi spirit-sha rule maps, hit detection, strength classification, structured evidence.
- Create `tests/test_bazi_spirits.py`: unit tests for spirit-sha output shape, key-position hits, and non-fatal behavior.
- Create `dongxuan_agent/bazi/discipline.py`: middle-image score normalization, capped spirit-sha deltas, discipline group scoring, cross-domain decision.
- Create `tests/test_bazi_discipline.py`: unit tests for discipline scoring without going through the full session pipeline.
- Modify `dongxuan_agent/bazi/imagery.py`: import and attach `spirit_sha_analysis`, `middle_image_scores`, `discipline_profile`, `llm_landing_constraints`.
- Modify `tests/test_bazi_imagery.py`: integration tests for major/career guidance fields and migration compatibility.
- Modify `bazi_prompt.md`: constrain model-assisted modern landing and web-assisted professional association to `discipline_profile`.
- Modify `tests/test_bazi_prompt_policy.py`: prompt policy tests for the new constraints.
- Optionally modify `dongxuan_agent/bazi/__init__.py`: export `build_bazi_spirit_sha_analysis` only if tests or wrappers need public import.

## Task 1: Add Bazi Spirit-Sha Analysis

**Files:**
- Create: `dongxuan_agent/bazi/spirits.py`
- Create: `tests/test_bazi_spirits.py`
- Optional Modify: `dongxuan_agent/bazi/__init__.py`

- [ ] **Step 1: Write failing tests for Bazi spirit-sha structure**

Add `tests/test_bazi_spirits.py`:

```python
from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi.spirits import build_bazi_spirit_sha_analysis
from dongxuan_agent.bazi_analysis import build_year_analysis_hints


def _payload():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()
    payload["analysis_hints"] = build_year_analysis_hints(chart, 2025)
    return payload


def test_bazi_spirit_sha_analysis_has_structured_active_hits():
    result = build_bazi_spirit_sha_analysis(_payload())

    assert result["scoring_policy"].startswith("神煞为辅助加权")
    assert result["active"]
    assert result["uncertainty"]
    for item in result["active"]:
        assert set(item) >= {
            "name",
            "value",
            "value_type",
            "basis",
            "hit_positions",
            "strength",
            "supports",
            "avoid",
            "evidence",
        }
        assert item["strength"] in {"strong", "medium", "weak"}
        assert item["supports"]
        assert item["avoid"]
        assert item["evidence"]


def test_bazi_spirit_sha_hits_current_luck_and_flow_year_positions():
    result = build_bazi_spirit_sha_analysis(_payload())
    locations = {
        location
        for item in result["active"]
        for location in item["hit_positions"]
    }

    assert "当前大运支" in locations or "当前大运干" in locations
    assert "目标流年支" in locations or "目标流年干" in locations


def test_bazi_spirit_sha_omits_non_hits_from_active_scoring():
    result = build_bazi_spirit_sha_analysis(_payload())

    assert all(item["hit_positions"] for item in result["active"])
    assert all(item["score_delta"] <= 0.2 for item in result["active"])
```

- [ ] **Step 2: Run the spirit-sha tests and verify they fail**

Run:

```bash
pytest tests/test_bazi_spirits.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'dongxuan_agent.bazi.spirits'`.

- [ ] **Step 3: Implement `dongxuan_agent/bazi/spirits.py`**

Create `dongxuan_agent/bazi/spirits.py`:

```python
from __future__ import annotations

from typing import Any

from ..constants import DAY_NOBLEMAN, STEM_LODGING_BRANCH
from .chart import HIDDEN_STEMS


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


def build_bazi_spirit_sha_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        rules = _spirit_rules(payload)
        positions = _positions(payload)
        active = [_active_hit(rule, positions, payload) for rule in rules]
        active = [item for item in active if item["hit_positions"]]
        return {
            "active": active,
            "scoring_policy": "神煞为辅助加权，总贡献受上限约束，不能覆盖强弱、格局、病药。",
            "uncertainty": [
                "八字神煞 V1 只覆盖专业/职业识别相关神煞，且只作中间画像辅助加权。",
                "学堂、天德、月德等神煞存在派别差异，V1 输出规则来源字段并保留不确定项。",
            ],
        }
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "active": [],
            "scoring_policy": "神煞为辅助加权，总贡献受上限约束，不能覆盖强弱、格局、病药。",
            "uncertainty": [f"八字神煞计算失败，已跳过神煞辅助：{exc}"],
        }


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


def _positions(payload: dict[str, Any]) -> list[dict[str, str]]:
    positions = []
    for pillar in payload.get("pillars", []):
        positions.append({"location": pillar["name"] + "干", "value": pillar["stem"], "value_type": "stem"})
        positions.append({"location": pillar["name"] + "支", "value": pillar["branch"], "value_type": "branch"})
    current_luck = (payload.get("analysis_hints") or {}).get("current_luck") or {}
    if current_luck.get("ganzhi"):
        positions.append({"location": "当前大运干", "value": current_luck["ganzhi"][0], "value_type": "stem"})
        positions.append({"location": "当前大运支", "value": current_luck["ganzhi"][1], "value_type": "branch"})
    flow_year = (payload.get("analysis_hints") or {}).get("flow_year") or {}
    if flow_year.get("ganzhi"):
        positions.append({"location": "目标流年干", "value": flow_year["ganzhi"][0], "value_type": "stem"})
        positions.append({"location": "目标流年支", "value": flow_year["ganzhi"][1], "value_type": "branch"})
    return positions


def _active_hit(rule: dict[str, str], positions: list[dict[str, str]], payload: dict[str, Any]) -> dict[str, Any]:
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
                "text": f"{rule['name']}命中{ '、'.join(hits) if hits else '无关键位置' }。",
            }
        ],
    }


def _hit_strength(hits: list[str]) -> str:
    if any(item in {"日柱支", "日柱干", "月柱支", "月柱干", "当前大运支", "当前大运干", "目标流年支", "目标流年干"} for item in hits):
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
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
pytest tests/test_bazi_spirits.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add dongxuan_agent/bazi/spirits.py tests/test_bazi_spirits.py
git commit -m "Add bazi spirit-sha analysis"
```

## Task 2: Add Discipline Profile Scoring

**Files:**
- Create: `dongxuan_agent/bazi/discipline.py`
- Create: `tests/test_bazi_discipline.py`

- [ ] **Step 1: Write failing discipline profile tests**

Add `tests/test_bazi_discipline.py`:

```python
from dongxuan_agent.bazi.discipline import build_discipline_profile


def test_discipline_profile_scores_cross_domain_when_groups_are_close():
    middle_scores = {
        "信息处理": {"final_score": 1.5, "evidence": ["信息处理成立"]},
        "公共传播": {"final_score": 1.4, "evidence": ["公共传播成立"]},
        "文本表达": {"final_score": 1.2, "evidence": ["文本表达成立"]},
    }
    result = build_discipline_profile(middle_scores, question="适合什么专业")

    assert result["cross_domain"] is True
    assert result["groups"][0]["name"] in {"information_data", "media_communication"}
    assert "不得强行归为纯文或纯理" in result["constraints_for_llm"]


def test_discipline_profile_keeps_strong_engineering_dominant_with_humanities_spirit():
    middle_scores = {
        "工程系统": {"final_score": 2.0, "evidence": ["金土结构强"]},
        "技能输出": {"final_score": 1.8, "evidence": ["食伤项目输出"]},
        "文本表达": {"final_score": 0.9, "evidence": ["文昌辅助，但结构弱"]},
    }
    result = build_discipline_profile(middle_scores, question="高考后学什么专业")

    assert result["groups"][0]["name"] == "stem_engineering"
    assert result["groups"][0]["score"] > 2.5
    assert result["cross_domain"] is False


def test_discipline_profile_has_structured_group_evidence():
    middle_scores = {
        "制度法理": {"final_score": 1.4, "evidence": ["官印规则成立"]},
        "信息处理": {"final_score": 1.3, "evidence": ["信息处理成立"]},
    }
    result = build_discipline_profile(middle_scores, question="职业方向")

    for group in result["groups"]:
        assert set(group) >= {
            "name",
            "score",
            "supporting_images",
            "spirit_factors",
            "structural_evidence",
            "weakening_factors",
            "confidence",
        }
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
pytest tests/test_bazi_discipline.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'dongxuan_agent.bazi.discipline'`.

- [ ] **Step 3: Implement `dongxuan_agent/bazi/discipline.py`**

Create `dongxuan_agent/bazi/discipline.py`:

```python
from __future__ import annotations

from typing import Any


DISCIPLINE_GROUPS = {
    "humanities_text": ["文本表达", "人文研究", "研究专精"],
    "law_public_policy": ["制度法理", "规则训练", "文本表达"],
    "stem_engineering": ["工程系统", "技能输出", "规则训练"],
    "information_data": ["信息处理", "工程系统", "研究专精"],
    "business_management": ["资源经营", "制度法理", "信息处理"],
    "media_communication": ["公共传播", "文本表达", "艺术设计"],
    "education_training": ["教育训练", "文本表达", "研究专精"],
    "arts_design": ["艺术设计", "文本表达", "技能输出"],
    "health_life_science": ["生命健康", "规则训练", "教育训练"],
}

CROSS_DOMAIN_PAIRS = {
    frozenset(("information_data", "media_communication")): "信息处理与传播表达的交叉型方向",
    frozenset(("education_training", "information_data")): "教育训练与信息技术的交叉型方向",
    frozenset(("law_public_policy", "information_data")): "制度法理与信息治理的交叉型方向",
    frozenset(("business_management", "information_data")): "经营管理与数据平台的交叉型方向",
    frozenset(("arts_design", "stem_engineering")): "设计表达与工程系统的交叉型方向",
    frozenset(("health_life_science", "education_training")): "生命健康与教育训练的交叉型方向",
    frozenset(("health_life_science", "humanities_text")): "身心健康与人文理解的交叉型方向",
}


def build_middle_image_scores(
    base_scores: dict[str, dict[str, Any]],
    spirit_sha_analysis: dict[str, Any],
    question: str = "",
) -> dict[str, dict[str, Any]]:
    result = {
        name: {
            "base_score": round(float(item.get("score", item.get("final_score", 0))), 2),
            "spirit_delta": 0.0,
            "question_delta": _question_delta(name, question),
            "final_score": 0.0,
            "evidence": list(item.get("evidence", item.get("reasons", []))),
        }
        for name, item in base_scores.items()
    }
    for hit in spirit_sha_analysis.get("active", []):
        delta = min(float(hit.get("score_delta", 0)), 0.2)
        for image in hit.get("supports", []):
            if image not in result:
                result[image] = {
                    "base_score": 0.0,
                    "spirit_delta": 0.0,
                    "question_delta": _question_delta(image, question),
                    "final_score": 0.0,
                    "evidence": [],
                }
            if result[image]["base_score"] <= 0:
                capped_delta = min(delta, 0.08)
            else:
                capped_delta = delta
            result[image]["spirit_delta"] = round(min(result[image]["spirit_delta"] + capped_delta, 0.35), 2)
            result[image]["evidence"].append(f"{hit['name']}辅助增强{image}：{hit['avoid']}")
    for item in result.values():
        item["final_score"] = round(item["base_score"] + item["spirit_delta"] + item["question_delta"], 2)
    return result


def build_discipline_profile(middle_image_scores: dict[str, dict[str, Any]], question: str = "") -> dict[str, Any]:
    groups = []
    for group_name, images in DISCIPLINE_GROUPS.items():
        hits = [image for image in images if middle_image_scores.get(image, {}).get("final_score", 0) > 0]
        score = round(sum(middle_image_scores[image]["final_score"] for image in hits), 2)
        if score <= 0:
            continue
        groups.append({
            "name": group_name,
            "score": score,
            "supporting_images": hits,
            "spirit_factors": [
                evidence
                for image in hits
                for evidence in middle_image_scores[image].get("evidence", [])
                if "辅助增强" in evidence
            ],
            "structural_evidence": [
                evidence
                for image in hits
                for evidence in middle_image_scores[image].get("evidence", [])
                if "辅助增强" not in evidence
            ],
            "weakening_factors": _weakening_factors(group_name, middle_image_scores),
            "confidence": _confidence(score),
        })
    groups.sort(key=lambda item: item["score"], reverse=True)
    top_names = [item["name"] for item in groups[:3]]
    cross_domain, mode = _cross_domain(top_names, groups, question)
    return {
        "groups": groups,
        "cross_domain": cross_domain,
        "recommended_mode": mode,
        "constraints_for_llm": [
            "不得强行归为纯文或纯理",
            "只能从高分族群组合联想到现代专业/职业",
            "最多输出两个现实落点",
            "联网检索只能用于解释现代专业实际学习内容，不得覆盖命盘画像裁决",
            "不得由单一神煞、五行或十神直接定专业",
        ],
    }


def _question_delta(name: str, question: str) -> float:
    mapping = {
        "文本表达": ("写作", "语言", "文学", "论文", "新闻", "传播"),
        "制度法理": ("法律", "法学", "公务", "政策", "制度"),
        "工程系统": ("工程", "硬件", "系统", "设备"),
        "信息处理": ("数据", "软件", "计算机", "信息", "算法"),
        "教育训练": ("教育", "师范", "教学", "课程"),
        "公共传播": ("传媒", "传播", "运营", "内容"),
        "艺术设计": ("设计", "艺术", "审美", "视觉"),
        "生命健康": ("医学", "护理", "心理", "健康", "生命"),
    }
    return 0.2 if any(keyword in question for keyword in mapping.get(name, ())) else 0.0


def _weakening_factors(group_name: str, scores: dict[str, dict[str, Any]]) -> list[str]:
    if group_name == "humanities_text" and scores.get("工程系统", {}).get("final_score", 0) > scores.get("文本表达", {}).get("final_score", 0) + 0.8:
        return ["工程系统明显强于文本表达，纯文本人文方向降级。"]
    if group_name == "stem_engineering" and scores.get("工程系统", {}).get("final_score", 0) <= 0:
        return ["缺少工程系统画像，理工工程方向不能作为主落点。"]
    return []


def _confidence(score: float) -> str:
    if score >= 3:
        return "high"
    if score >= 1.5:
        return "medium"
    return "low"


def _cross_domain(top_names: list[str], groups: list[dict[str, Any]], question: str) -> tuple[bool, str]:
    if len(groups) < 2:
        return False, groups[0]["name"] if groups else "证据不足"
    top_two = groups[:2]
    pair = frozenset((top_two[0]["name"], top_two[1]["name"]))
    if pair in CROSS_DOMAIN_PAIRS and abs(top_two[0]["score"] - top_two[1]["score"]) <= 0.8:
        return True, CROSS_DOMAIN_PAIRS[pair]
    if abs(top_two[0]["score"] - top_two[1]["score"]) <= 0.4:
        return True, f"{top_two[0]['name']} 与 {top_two[1]['name']} 的交叉型方向"
    if any(keyword in question for keyword in ("交叉", "复合", "跨学科", "新兴")):
        return True, f"{top_two[0]['name']} 与 {top_two[1]['name']} 的交叉型方向"
    return False, top_two[0]["name"]
```

- [ ] **Step 4: Run discipline tests and verify pass**

Run:

```bash
pytest tests/test_bazi_discipline.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 2**

```bash
git add dongxuan_agent/bazi/discipline.py tests/test_bazi_discipline.py
git commit -m "Add bazi discipline profile scoring"
```

## Task 3: Integrate Spirit-Sha And Discipline Profile Into Imagery

**Files:**
- Modify: `dongxuan_agent/bazi/imagery.py`
- Modify: `tests/test_bazi_imagery.py`

- [ ] **Step 1: Add failing integration tests**

Append to `tests/test_bazi_imagery.py`:

```python
def test_major_identification_includes_spirit_sha_and_discipline_profile():
    result = build_imagery_analysis(_payload("他2024年高考后适合什么专业"))
    guidance = result["answer_guidance"]["major_or_career_identification"]

    assert guidance["spirit_sha_analysis"]["scoring_policy"].startswith("神煞为辅助加权")
    assert "middle_image_scores" in guidance
    assert "discipline_profile" in guidance
    assert guidance["discipline_profile"]["groups"]
    assert "不得强行归为纯文或纯理" in guidance["discipline_profile"]["constraints_for_llm"]
    assert guidance["llm_landing_constraints"]


def test_spirit_sha_does_not_replace_existing_landing_evidence():
    result = build_imagery_analysis(_payload("他2024年高考后适合什么专业"))
    guidance = result["answer_guidance"]["major_or_career_identification"]

    assert guidance["landing_evidence"]["supported"]
    assert guidance["symbolic_layers"]["middle_images"]
    assert all(
        item["score"] >= 0
        for item in guidance["discipline_profile"]["groups"]
    )
```

- [ ] **Step 2: Run the new imagery tests and verify they fail**

Run:

```bash
pytest tests/test_bazi_imagery.py::test_major_identification_includes_spirit_sha_and_discipline_profile tests/test_bazi_imagery.py::test_spirit_sha_does_not_replace_existing_landing_evidence -v
```

Expected: FAIL with missing `spirit_sha_analysis` or `discipline_profile`.

- [ ] **Step 3: Modify `dongxuan_agent/bazi/imagery.py` imports**

Add imports near the top:

```python
from .discipline import build_discipline_profile, build_middle_image_scores
from .spirits import build_bazi_spirit_sha_analysis
```

- [ ] **Step 4: Modify `_answer_guidance()` to attach new fields**

Replace the current return body for `major_or_career_identification` with this structure, preserving existing fields:

```python
    spirit_sha = build_bazi_spirit_sha_analysis(payload)
    base_middle_scores = _base_middle_image_scores(payload)
    middle_image_scores = build_middle_image_scores(base_middle_scores, spirit_sha, payload.get("question") or "")
    discipline_profile = build_discipline_profile(middle_image_scores, payload.get("question") or "")
    return {
        "major_or_career_identification": {
            "rule": "专业/职业/行业识别题必须先合参五行旺衰、干支作用、病药喜忌、神煞辅助和知识库象义，再归纳现实落点。",
            "max_real_world_landings": 2,
            "knowledge_query_terms": _knowledge_query_terms(payload, main, secondary),
            "knowledge_sources": _knowledge_sources(_knowledge_query_terms(payload, main, secondary)),
            "symbolic_layers": _symbolic_layers(payload),
            "landing_evidence": _landing_evidence(payload),
            "symbolic_dynamics": _symbolic_dynamics(payload),
            "direction_profile": _direction_profile(payload, main, secondary),
            "spirit_sha_analysis": spirit_sha,
            "middle_image_scores": middle_image_scores,
            "discipline_profile": discipline_profile,
            "llm_landing_constraints": discipline_profile["constraints_for_llm"],
            "evidence": _season_strength_evidence(payload),
            "forbidden": "禁止输出五行/十神/神煞等于现实专业或行业的直接映射；禁止由工具预设专业名。",
        }
    }
```

- [ ] **Step 5: Add `_base_middle_image_scores()` helper in `imagery.py`**

Place this helper after `_middle_image_strengths()`:

```python
def _base_middle_image_scores(payload: dict) -> dict[str, dict]:
    dynamics = _symbolic_dynamics(payload)
    active_middle = _active_middle_image_names(payload, dynamics)
    strengths = _middle_image_strengths(payload, active_middle)
    return {
        name: {
            "score": item.get("score", 0),
            "evidence": item.get("reasons", []),
        }
        for name, item in strengths.items()
    }
```

- [ ] **Step 6: Run focused imagery tests**

Run:

```bash
pytest tests/test_bazi_imagery.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```bash
git add dongxuan_agent/bazi/imagery.py tests/test_bazi_imagery.py
git commit -m "Integrate discipline profile into bazi imagery"
```

## Task 4: Update Prompt Constraints For Model-Assisted Landing

**Files:**
- Modify: `bazi_prompt.md`
- Modify: `tests/test_bazi_prompt_policy.py`

- [ ] **Step 1: Write failing prompt policy test**

Append to `tests/test_bazi_prompt_policy.py`:

```python
def test_bazi_prompt_constrains_model_assisted_major_landing():
    text = PROMPT.read_text(encoding="utf-8")

    assert "discipline_profile" in text
    assert "神煞只作辅助加权" in text
    assert "不得强行归为纯文或纯理" in text
    assert "联网检索只能用于解释现代专业实际学习内容" in text
    assert "不得覆盖命盘画像裁决" in text
```

- [ ] **Step 2: Run the prompt test and verify it fails**

Run:

```bash
pytest tests/test_bazi_prompt_policy.py::test_bazi_prompt_constrains_model_assisted_major_landing -v
```

Expected: FAIL with missing prompt phrases.

- [ ] **Step 3: Modify `bazi_prompt.md` hard rules**

Add these bullets under `## 收敛规则` after the existing professional-identification bullets:

```markdown
- 专业/职业/行业识别题若有 `discipline_profile`，必须以其高分族群、`supporting_images`、`structural_evidence` 和 `weakening_factors` 作为现实落点边界。
- 神煞只作辅助加权；文昌、学堂、华盖、桃花、驿马、贵人、禄神、将星、羊刃等不得直接等同文科、理工、专业、职业或结果。
- 不得强行归为纯文或纯理；若 `discipline_profile.cross_domain` 为 true，应优先按交叉型专业/职业方向解释。
- 联网检索只能用于解释现代专业实际学习内容、职业任务和现实名称，不得覆盖命盘画像裁决。
- 现实落点必须回指 `discipline_profile.groups`、`middle_image_scores` 和 `spirit_sha_analysis.active`；神煞证据只能写成辅助增强，不可写成主因。
```

- [ ] **Step 4: Modify `bazi_prompt.md` professional output format**

In `## 专业/职业识别输出格式`, add this bullet under `## 抽象取象画像`:

```markdown
- 专业族群画像：引用 `imagery_analysis.answer_guidance.major_or_career_identification.discipline_profile`，说明高分族群、是否交叉型、哪些中间画像成立，哪些画像被削弱。
```

Add this bullet under `## 证据`:

```markdown
- 神煞辅助：如有 `spirit_sha_analysis.active`，只说明它增强了哪些中间画像；不得写成“因某神煞所以是某专业”。
```

- [ ] **Step 5: Run prompt policy tests**

Run:

```bash
pytest tests/test_bazi_prompt_policy.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

```bash
git add bazi_prompt.md tests/test_bazi_prompt_policy.py
git commit -m "Constrain model-assisted bazi major landing"
```

## Task 5: Full Verification And Compatibility Pass

**Files:**
- Modify only if failures reveal necessary small compatibility fixes.

- [ ] **Step 1: Run all Bazi-related tests**

Run:

```bash
pytest tests/test_bazi*.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run:

```bash
pytest -v
```

Expected: PASS.

- [ ] **Step 3: Inspect the major/career output manually**

Run:

```bash
python - <<'PY'
from dongxuan_agent.bazi.context import build_bazi_context
payload = build_bazi_context(
    "2006-12-18 12:30:00",
    timezone="Asia/Shanghai",
    gender="男",
    target_year=2025,
    question="高考后适合什么专业，是否有文理交叉方向",
)
guidance = payload["imagery_analysis"]["answer_guidance"]["major_or_career_identification"]
print(guidance["discipline_profile"]["recommended_mode"])
print([item["name"] for item in guidance["discipline_profile"]["groups"][:3]])
print(guidance["llm_landing_constraints"])
PY
```

Expected: prints a recommended mode, top discipline groups, and the LLM constraints. It must not print a long modern major candidate list from local tooling.

- [ ] **Step 4: Check git diff for scope**

Run:

```bash
git status --short
git diff --stat HEAD
```

Expected: only files from this plan are modified since the previous task commit.

- [ ] **Step 5: Commit verification fixes if any**

If Task 5 required fixes, commit them:

```bash
git add dongxuan_agent/bazi tests bazi_prompt.md
git commit -m "Stabilize bazi cross-discipline imagery"
```

If no fixes were needed, do not create an empty commit.

