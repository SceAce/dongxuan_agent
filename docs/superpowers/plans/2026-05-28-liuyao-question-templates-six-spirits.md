# Liuyao Question Templates and Six Spirits Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Liuyao v4 question templates and six-spirit auxiliary imagery without letting six spirits or reserved spirit-sha become final judgment authority.

**Architecture:** Add focused Liuyao modules for templates and six spirits, then wire them through `judgment.enrich_payload`. Keep v3 imagery selection stable and extend it with bounded template evidence. Update schema/prompt contracts and tests.

**Tech Stack:** Python 3.13, pytest, existing `dongxuan_agent.liuyao` package, Markdown prompt/spec docs.

---

## File Structure

- Create `dongxuan_agent/liuyao/templates.py`: deterministic question-template dictionary and `build_question_template`.
- Create `dongxuan_agent/liuyao/six_spirits.py`: day-stem six-spirit assignment and line attachment.
- Modify `dongxuan_agent/liuyao/judgment.py`: add template and six-spirit enrichment, prompt contract fields, auxiliary marks.
- Modify `dongxuan_agent/liuyao/chart.py`: upgrade schema to `liuyao_chart_v4`.
- Modify `dongxuan_agent/liuyao/imagery.py`: allow `build_useful_god_selection` to consume template evidence.
- Modify `liuyao_prompt.md`: add template and six-spirit policy.
- Add/modify tests under `tests/`.

## Task 1: Question Templates

**Files:**
- Create: `dongxuan_agent/liuyao/templates.py`
- Test: `tests/test_liuyao_templates.py`

- [ ] **Step 1: Write failing template tests**

```python
from dongxuan_agent.liuyao.templates import build_question_template


def test_career_work_template_selects_main_and_auxiliary_images():
    template = build_question_template("事业/工作", "问工作 offer 合同什么时候下来")

    assert template["template_id"] == "career_work"
    assert template["domain"] == "事业/工作"
    assert "question_context.domain" in template["selected_by"]
    assert any(item["six_relative"] == "官鬼" for item in template["main_images"])
    assert any(item["six_relative"] == "父母" for item in template["auxiliary_images"])
    assert any("工作 + 合同" in rule for rule in template["conflict_rules"])
    assert "模板只决定取象入口，不决定最终成败。" in template["must_not_mix"]


def test_unknown_domain_returns_uncategorized_template_contract():
    template = build_question_template("综合/未分类", "随便问问")

    assert template["template_id"] == "uncategorized"
    assert template["domain"] == "综合/未分类"
    assert template["main_images"] == []
    assert template["auxiliary_images"] == []
    assert template["secondary_templates"] == []
```

- [ ] **Step 2: Verify tests fail**

Run: `uv run pytest tests/test_liuyao_templates.py -v`

Expected: FAIL with `ModuleNotFoundError` for `dongxuan_agent.liuyao.templates`.

- [ ] **Step 3: Implement templates module**

Create `dongxuan_agent/liuyao/templates.py` with:

```python
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
    "模板不能引入八字或大六壬逻辑。",
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
        "must_not_mix": MUST_NOT_MIX,
    }
```

- [ ] **Step 4: Run template tests**

Run: `uv run pytest tests/test_liuyao_templates.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/templates.py tests/test_liuyao_templates.py
git commit -m "Add liuyao question templates"
```

## Task 2: Six Spirits

**Files:**
- Create: `dongxuan_agent/liuyao/six_spirits.py`
- Test: `tests/test_liuyao_six_spirits.py`

- [ ] **Step 1: Write failing six-spirit tests**

```python
from dongxuan_agent.liuyao.six_spirits import assign_six_spirits


def test_ren_day_starts_with_xuanwu_from_initial_line():
    derived_lines = [
        {"position": 1, "six_relative": "父母", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": True, "moving": False},
        {"position": 2, "six_relative": "子孙", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": True},
        {"position": 3, "six_relative": "官鬼", "role": "应", "is_shi": False, "is_ying": True, "is_candidate_useful_god": True, "moving": False},
        {"position": 4, "six_relative": "妻财", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
        {"position": 5, "six_relative": "子孙", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
        {"position": 6, "six_relative": "兄弟", "role": "世", "is_shi": True, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
    ]

    result = assign_six_spirits("壬寅", derived_lines)

    assert result["day_stem"] == "壬"
    assert result["start_spirit"] == "玄武"
    assert [line["spirit"] for line in result["lines"]] == ["玄武", "青龙", "朱雀", "勾陈", "螣蛇", "白虎"]
    assert result["scope"] == "辅助取象，不作主裁决"
    assert result["lines"][0]["attached_to"]["six_relative"] == "父母"
    assert "不能单凭玄武断欺瞒" in result["lines"][0]["cautions"]
```

- [ ] **Step 2: Verify test fails**

Run: `uv run pytest tests/test_liuyao_six_spirits.py -v`

Expected: FAIL with `ModuleNotFoundError` for `dongxuan_agent.liuyao.six_spirits`.

- [ ] **Step 3: Implement six spirits module**

Create `dongxuan_agent/liuyao/six_spirits.py` with:

```python
from __future__ import annotations

SIX_SPIRIT_ORDER = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]

START_BY_DAY_STEM = {
    "甲": "青龙",
    "乙": "青龙",
    "丙": "朱雀",
    "丁": "朱雀",
    "戊": "勾陈",
    "己": "螣蛇",
    "庚": "白虎",
    "辛": "白虎",
    "壬": "玄武",
    "癸": "玄武",
}

SIX_SPIRIT_IMAGERY = {
    "青龙": {"imagery": ["喜庆", "财喜", "文雅", "顺遂"], "cautions": ["不能单凭青龙断吉"]},
    "朱雀": {"imagery": ["口舌", "消息", "文书", "表达"], "cautions": ["需依附具体爻和六亲，不得单独断口舌"]},
    "勾陈": {"imagery": ["迟滞", "田土", "牵连", "旧事"], "cautions": ["不能单凭勾陈断拖延，需合看动静和月日"]},
    "螣蛇": {"imagery": ["虚惊", "疑虑", "缠绕", "怪异"], "cautions": ["不能单凭螣蛇断异常或欺诈"]},
    "白虎": {"imagery": ["伤病", "压力", "冲突", "急迫"], "cautions": ["不能单凭白虎断凶"]},
    "玄武": {"imagery": ["隐情", "暗昧", "欺瞒", "私下"], "cautions": ["不能单凭玄武断欺瞒"]},
}


def assign_six_spirits(day_gz: str, derived_lines: list[dict]) -> dict:
    day_stem = day_gz[0]
    start_spirit = START_BY_DAY_STEM[day_stem]
    start_index = SIX_SPIRIT_ORDER.index(start_spirit)
    lines = []
    for offset, line in enumerate(sorted(derived_lines, key=lambda item: item["position"])):
        spirit = SIX_SPIRIT_ORDER[(start_index + offset) % len(SIX_SPIRIT_ORDER)]
        info = SIX_SPIRIT_IMAGERY[spirit]
        lines.append(
            {
                "position": line["position"],
                "spirit": spirit,
                "imagery": list(info["imagery"]),
                "attached_to": {
                    "six_relative": line["six_relative"],
                    "role": line["role"],
                    "is_shi": line["is_shi"],
                    "is_ying": line["is_ying"],
                    "is_candidate_useful_god": line["is_candidate_useful_god"],
                    "moving": line["moving"],
                },
                "interpretation_scope": [
                    "只用于说明该爻象意呈现方式。",
                    "必须依附六亲、世应、用神、动变、旺衰字段使用。",
                ],
                "cautions": list(info["cautions"]),
            }
        )
    return {
        "start_basis": "按日干起六神",
        "day_stem": day_stem,
        "start_spirit": start_spirit,
        "scope": "辅助取象，不作主裁决",
        "lines": lines,
    }
```

- [ ] **Step 4: Run six-spirit tests**

Run: `uv run pytest tests/test_liuyao_six_spirits.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/six_spirits.py tests/test_liuyao_six_spirits.py
git commit -m "Add liuyao six spirits"
```

## Task 3: v4 Payload Integration

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/imagery.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_imagery.py`

- [ ] **Step 1: Write failing v4 integration tests**

Update `tests/test_liuyao_chart.py` expectations:

```python
assert chart["schema"] == "liuyao_chart_v4"
assert "question_template" in chart
assert "six_spirits" in chart
assert "auxiliary_marks" in chart
assert chart["question_template"]["template_id"] == "career_work"
assert chart["six_spirits"]["scope"] == "辅助取象，不作主裁决"
assert chart["auxiliary_marks"]["enabled"] == []
assert all("six_spirit" in line for line in chart["derived_lines"])
assert "question_template" in chart["prompt_contract"]["must_use_fields"]
assert "six_spirits" in chart["prompt_contract"]["must_use_fields"]
```

Update `tests/test_liuyao_imagery.py` layered test:

```python
assert payload["question_template"]["template_id"] == "career_work"
assert selection["far_symbol_focus"][0]["source"] in {"template_main", "token_match"}
assert any(item.get("source") == "template_auxiliary" and item["six_relative"] == "父母" for item in selection["far_symbol_focus"])
```

- [ ] **Step 2: Verify tests fail**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_imagery.py -v`

Expected: FAIL because schema is still v3 and v4 fields are absent.

- [ ] **Step 3: Wire templates, six spirits, auxiliary marks**

Modify `judgment.enrich_payload`:

```python
from .six_spirits import assign_six_spirits
from .templates import build_question_template


def enrich_payload(payload: dict) -> dict:
    derived_lines = build_derived_lines(payload)
    question_template = build_question_template(payload["question_context"]["domain"], payload["input"]["question"])
    useful_gods = build_useful_god_analysis(payload, derived_lines)
    imagery_context = build_imagery_context(payload["input"]["question"], useful_gods["domain"])
    useful_god_selection = build_useful_god_selection(payload, derived_lines, useful_gods, imagery_context, question_template)
    six_spirits = assign_six_spirits(payload["calendar"]["day_gz"], derived_lines)
    _attach_six_spirits_to_lines(derived_lines, six_spirits)
    relations = build_relations(payload, derived_lines, useful_gods)
    payload["derived_lines"] = derived_lines
    payload["question_template"] = question_template
    payload["useful_god_analysis"] = useful_gods
    payload["imagery_context"] = imagery_context
    payload["useful_god_selection"] = useful_god_selection
    payload["six_spirits"] = six_spirits
    payload["auxiliary_marks"] = auxiliary_marks()
    payload["relations"] = relations
    payload["judgment_frame"] = judgment_frame(bool(payload["hexagram"]["moving_lines"]))
    payload["prompt_contract"] = prompt_contract()
    return payload
```

Add helpers:

```python
def _attach_six_spirits_to_lines(derived_lines: list[dict], six_spirits: dict) -> None:
    by_position = {line["position"]: line for line in six_spirits["lines"]}
    for line in derived_lines:
        spirit = by_position[line["position"]]
        line["six_spirit"] = {
            "spirit": spirit["spirit"],
            "imagery": spirit["imagery"],
            "cautions": spirit["cautions"],
        }


def auxiliary_marks() -> dict:
    return {
        "enabled": [],
        "reserved": ["驿马", "桃花", "贵人"],
        "scope": "预留字段；当前不计算神煞，不得在 prompt 中编造命中。",
    }
```

Update `prompt_contract.must_use_fields` to include `question_template` and `six_spirits`; update `must_not_infer` to include `未实现的神煞命中`.

Modify `chart.py` schema string to `liuyao_chart_v4`.

- [ ] **Step 4: Extend useful-god selection with template evidence**

Change signature:

```python
def build_useful_god_selection(payload, derived_lines, useful_god_analysis, imagery_context, question_template=None):
```

Update `_far_symbol_focus` to include template main and auxiliary images with `source`:

```python
def _far_symbol_focus(useful_god_analysis: dict, imagery_context: dict, question_template: dict | None = None) -> list[dict]:
    by_relative = {candidate["six_relative"]: candidate for candidate in useful_god_analysis["candidates"]}
    result = []
    seen = set()
    if question_template:
        for item, source in _template_focus_items(question_template):
            relative = item["six_relative"]
            if relative == "世应" or relative in seen or relative not in by_relative:
                continue
            candidate = by_relative[relative]
            result.append(
                {
                    "six_relative": relative,
                    "image": item["image"],
                    "matching_lines": [line["position"] for line in candidate["matching_lines"]],
                    "reason": item["reason"],
                    "source": source,
                }
            )
            seen.add(relative)
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
                "source": "token_match",
            }
        )
        seen.add(relative)
    return result


def _template_focus_items(question_template: dict) -> list[tuple[dict, str]]:
    items = [(item, "template_main") for item in question_template.get("main_images", [])]
    items.extend((item, "template_auxiliary") for item in question_template.get("auxiliary_images", []))
    return items
```

- [ ] **Step 5: Run v4 integration tests**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_imagery.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add dongxuan_agent/liuyao/chart.py dongxuan_agent/liuyao/judgment.py dongxuan_agent/liuyao/imagery.py tests/test_liuyao_chart.py tests/test_liuyao_imagery.py
git commit -m "Integrate liuyao v4 templates and spirits"
```

## Task 4: Prompt Policy and Verification

**Files:**
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_prompt_policy.py`
- Modify: `tests/test_liuyao_session.py` if schema assertions require v4.

- [ ] **Step 1: Write failing prompt policy tests**

Add to `tests/test_liuyao_prompt_policy.py`:

```python
def test_liuyao_prompt_requires_templates_and_six_spirits_as_auxiliary_only():
    for text in ["question_template", "six_spirits", "辅助取象，不作主裁决", "青龙必吉", "白虎必凶", "玄武必欺瞒", "auxiliary_marks.enabled"]:
        assert text in PROMPT
    assert "不能单凭青龙断吉" in PROMPT
    assert "不能单凭白虎断凶" in PROMPT
    assert "不得在 prompt 中编造命中" in PROMPT
```

- [ ] **Step 2: Verify prompt test fails**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py -v`

Expected: FAIL until prompt text is updated.

- [ ] **Step 3: Update prompt**

Patch `liuyao_prompt.md`:

- Add hard-boundary bullets requiring `question_template` and `six_spirits`.
- Add hard-boundary bullets that six spirits are `辅助取象，不作主裁决`.
- Add hard-boundary bullets forbidding "青龙必吉", "白虎必凶", "玄武必欺瞒".
- Add `auxiliary_marks.enabled` rule: when empty, no spirit-sha is implemented and no hit may be fabricated.
- Update `用神定位`, `世应关系`, `动变作用`, `综合倾向`, and `不确定项` sections as specified.

- [ ] **Step 4: Run prompt/session tests**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py tests/test_liuyao_session.py -v`

Expected: PASS.

- [ ] **Step 5: Run full verification**

Run Liuyao tests:

```bash
uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_templates.py tests/test_liuyao_six_spirits.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v
```

Run full suite:

```bash
uv run pytest -q
```

Run boundary scan:

```bash
rg -n "strength_analysis|climate_analysis|pattern_analysis|remedy_analysis|god_candidates|luck_year_remedy|discipline_profile|four_lessons|transmissions|heavenly_officers|day_master_element" dongxuan_agent/liuyao liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py
```

Expected boundary scan: no problematic matches; `useful_god_candidates` remains acceptable.

Run CLI sample:

```bash
uv run python -m dongxuan_agent.liuyao_cli --hexagram "离之大有" --question "问工作 offer 合同什么时候下来" --datetime "2026-05-28 09:30:00" --format json
```

Expected:

- `schema = liuyao_chart_v4`
- `question_template.template_id = career_work`
- `useful_god_selection.selection_result.status = layered`
- `six_spirits.start_spirit = 玄武`
- `auxiliary_marks.enabled = []`

- [ ] **Step 6: Commit**

```bash
git add liuyao_prompt.md tests/test_liuyao_prompt_policy.py tests/test_liuyao_session.py
git commit -m "Optimize liuyao v4 prompt policy"
```

