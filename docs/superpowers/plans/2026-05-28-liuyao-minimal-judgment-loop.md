# Liuyao Minimal Judgment Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Liuyao JSON to `liuyao_chart_v2` with derived line evidence, month/day strength, useful-god line location, relations, and a prompt-controlled minimal judgment loop.

**Architecture:** Add focused Liuyao-only modules for relation and strength logic, then assemble v2 fields in chart output. Keep chart construction in `chart.py`, preserve existing v1 chart fields, and update prompt/session tests after JSON fields exist.

**Tech Stack:** Python 3.11+, dataclasses, argparse, pytest, existing `uv run pytest` workflow.

---

## File Structure

- Create `dongxuan_agent/liuyao/relations.py`: branch relations, element relations, relation labels, changed-line return labels.
- Create `dongxuan_agent/liuyao/strength.py`: month element, 旺相休囚死, effective strength, over-strong/over-weak labels.
- Create `dongxuan_agent/liuyao/judgment.py`: derived lines, useful-god analysis, relation summaries, judgment frame, prompt contract.
- Modify `dongxuan_agent/liuyao/chart.py`: output `liuyao_chart_v2` and include new v2 fields.
- Modify `liuyao_prompt.md`: fixed minimal-loop prompt sections and unsupported-rule boundaries.
- Modify tests under `tests/test_liuyao_*.py`.

---

### Task 1: Relation And Seasonal Strength Primitives

**Files:**
- Create: `tests/test_liuyao_strength.py`
- Create: `dongxuan_agent/liuyao/relations.py`
- Create: `dongxuan_agent/liuyao/strength.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao.relations import branch_relation, element_relation, return_relation_label
from dongxuan_agent.liuyao.strength import effective_strength, extreme_state, seasonal_state


def test_si_month_maps_elements_to_wang_xiang_xiu_qiu_si():
    assert seasonal_state("火", "巳") == "旺"
    assert seasonal_state("土", "巳") == "相"
    assert seasonal_state("木", "巳") == "休"
    assert seasonal_state("水", "巳") == "囚"
    assert seasonal_state("金", "巳") == "死"


def test_branch_relation_supports_same_clash_and_combine_only():
    assert branch_relation("巳", "巳") == "same"
    assert branch_relation("巳", "亥") == "clash"
    assert branch_relation("寅", "亥") == "combine"
    assert branch_relation("巳", "酉") == "none"


def test_element_relation_is_directional():
    assert element_relation("木", "火") == "generates"
    assert element_relation("火", "木") == "generated_by"
    assert element_relation("水", "火") == "controls"
    assert element_relation("火", "水") == "controlled_by"
    assert element_relation("土", "土") == "same"


def test_return_relation_labels_changed_line_direction():
    assert return_relation_label("木", "火") == "回头生"
    assert return_relation_label("水", "火") == "回头克"
    assert return_relation_label("火", "火") == "比和"
    assert return_relation_label("火", "土") == "泄气"
    assert return_relation_label("金", "火") == "耗气"


def test_extreme_state_requires_multiple_clear_factors():
    assert extreme_state(
        "旺",
        support_factors=["日辰生扶", "动爻发动"],
        weakening_factors=[],
    ) == "over_strong"
    assert extreme_state(
        "死",
        support_factors=[],
        weakening_factors=["日辰克制", "旬空"],
    ) == "over_weak"
    assert extreme_state(
        "旺",
        support_factors=["日辰生扶"],
        weakening_factors=["旬空"],
    ) == "none"


def test_effective_strength_returns_coarse_labels():
    assert effective_strength("旺", ["日辰生扶"], []) == "strong"
    assert effective_strength("死", [], ["旬空"]) == "very_weak"
    assert effective_strength("休", [], []) == "balanced"
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_strength.py -v`

Expected: FAIL because `relations.py` and `strength.py` do not exist.

- [ ] **Step 3: Implement relation and strength primitives**

Implement:
- `BRANCH_ELEMENTS`
- `branch_relation(left_branch, right_branch)`
- `element_relation(actor_element, target_element)`
- `return_relation_label(actor_element, changed_element)`
- `seasonal_state(line_element, month_branch)`
- `effective_strength(seasonal, support_factors, weakening_factors)`
- `extreme_state(seasonal, support_factors, weakening_factors)`

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_strength.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/relations.py dongxuan_agent/liuyao/strength.py tests/test_liuyao_strength.py
git commit -m "Add liuyao strength primitives"
```

---

### Task 2: Judgment Derived Fields

**Files:**
- Create: `tests/test_liuyao_judgment.py`
- Create: `dongxuan_agent/liuyao/judgment.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao import build_liuyao_chart


def test_derived_lines_merge_line_najia_useful_god_and_strength():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert payload["schema"] == "liuyao_chart_v2"
    line = payload["derived_lines"][2]
    assert line["position"] == 3
    assert line["stem_branch"] == "己亥"
    assert line["six_relative"] == "官鬼"
    assert line["role"] == "应"
    assert line["is_ying"] is True
    assert line["is_candidate_useful_god"] is True
    assert line["month_state"]["seasonal_state"] == "囚"
    assert line["month_state"]["branch_relation"] == "clash"
    assert line["day_state"]["branch_relation"] == "combine"
    assert line["void_state"]["is_void"] is False
    assert line["effective_strength"] in {"very_strong", "strong", "balanced", "weak", "very_weak"}
    assert line["extreme_state"] in {"over_strong", "over_weak", "none"}
    assert line["strength_evidence"]


def test_useful_god_analysis_maps_candidates_to_matching_lines():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["useful_god_analysis"]
    primary = analysis["candidates"][0]
    assert primary["six_relative"] == "官鬼"
    assert primary["priority"] == "primary"
    assert primary["matching_lines"][0]["position"] == 3
    assert "候选用神不等于最终用神" in primary["selection_constraints"]


def test_relations_include_month_day_shi_ying_and_moving_effects():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    relations = payload["relations"]
    assert relations["month_day"]["month_branch"] == "巳"
    assert relations["month_day"]["by_line"][2]["month"]["seasonal_state"] == "囚"
    assert relations["shi_ying"]["shi_position"] == 6
    assert relations["shi_ying"]["ying_position"] == 3
    assert relations["shi_ying"]["summary"]
    moving = relations["moving_effects"][0]
    assert moving["actor_position"] == 2
    assert {target["target"] for target in moving["targets"]} >= {"shi", "ying", "candidate_useful_god"}
    assert moving["changed_line"]["return_label"] in {"回头生", "回头克", "比和", "泄气", "耗气", "无直接作用"}


def test_judgment_frame_and_prompt_contract_exist():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert payload["judgment_frame"]["mode"] == "minimal_loop"
    assert [step["name"] for step in payload["judgment_frame"]["steps"]] == [
        "question_domain",
        "locate_useful_gods",
        "check_shi_ying",
        "check_month_day_strength",
        "check_moving_changed_lines",
        "synthesize",
    ]
    assert "derived_lines" in payload["prompt_contract"]["must_use_fields"]
    assert "未实现的六神" in payload["prompt_contract"]["must_not_infer"]
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_judgment.py -v`

Expected: FAIL because v2 fields are not assembled.

- [ ] **Step 3: Implement judgment field assembly**

Implement in `judgment.py`:
- `build_derived_lines(payload)`
- `build_useful_god_analysis(payload, derived_lines)`
- `build_relations(payload, derived_lines, useful_god_analysis)`
- `judgment_frame(has_moving_lines)`
- `prompt_contract()`

This module should accept the already-built chart dictionary from `chart.py` and return only Liuyao-derived fields.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_judgment.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/judgment.py tests/test_liuyao_judgment.py
git commit -m "Add liuyao judgment fields"
```

---

### Task 3: Integrate V2 Chart Output

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_session.py`

- [ ] **Step 1: Update tests for v2 output**

Change existing Liuyao tests to expect `schema == "liuyao_chart_v2"` while keeping original chart-field assertions. Add assertions that CLI and session output contain v2 fields.

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: FAIL because `chart.py` still outputs v1 or lacks v2 fields.

- [ ] **Step 3: Integrate judgment fields in `LiuyaoChart.to_dict()`**

Update `to_dict()` to:
- build the existing base payload
- set `schema` to `liuyao_chart_v2`
- call judgment assembly
- add `derived_lines`, `useful_god_analysis`, `relations`, `judgment_frame`, and `prompt_contract`
- keep `lines`, `najia`, `palace`, `question_context`, and `analysis_hints`

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_judgment.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/chart.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py
git commit -m "Integrate liuyao v2 chart output"
```

---

### Task 4: Prompt Upgrade

**Files:**
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_session.py`
- Create: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Write failing prompt tests**

```python
from pathlib import Path


PROMPT = Path("liuyao_prompt.md").read_text(encoding="utf-8")


def test_liuyao_prompt_has_minimal_loop_sections():
    for section in ["卦体摘要", "用神定位", "世应关系", "旺衰与月日", "动变作用", "综合倾向", "不确定项"]:
        assert f"## {section}" in PROMPT


def test_liuyao_prompt_requires_v2_fields_and_forbids_unsupported_rules():
    for field in ["derived_lines", "useful_god_analysis", "relations.month_day", "relations.shi_ying", "relations.moving_effects"]:
        assert field in PROMPT
    for forbidden in ["六神", "飞伏", "三合局", "应期", "八字旺衰", "大六壬四课三传"]:
        assert forbidden in PROMPT
    assert "不得把旺直接视为吉" in PROMPT
    assert "不得把死直接视为凶" in PROMPT
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py -v`

Expected: FAIL because prompt is still v1 summary style.

- [ ] **Step 3: Update prompt**

Rewrite `liuyao_prompt.md` to:
- require v2 fields
- enforce fixed seven sections
- forbid unsupported rules
- require cautious tendency labels
- require evidence and uncertainty bullets

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py tests/test_liuyao_session.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add liuyao_prompt.md tests/test_liuyao_prompt_policy.py tests/test_liuyao_session.py
git commit -m "Upgrade liuyao prompt loop"
```

---

### Task 5: Full Verification

**Files:**
- Modify only files needed for verification fixes.

- [ ] **Step 1: Run Liuyao tests**

Run: `uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v`

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -q`

Expected: PASS.

- [ ] **Step 3: Run boundary scan**

Run: `rg -n "strength_analysis|climate_analysis|pattern_analysis|remedy_analysis|god_candidates|luck_year_remedy|discipline_profile|four_lessons|transmissions|heavenly_officers|day_master_element" dongxuan_agent/liuyao liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py`

Expected: no matches except prompt text that explicitly forbids unsupported external systems.

- [ ] **Step 4: Run example CLI**

Run: `uv run python -m dongxuan_agent.liuyao_cli --hexagram "离之大有" --question "问工作" --datetime "2026-05-28 09:30:00" --format json`

Expected: JSON includes `schema = liuyao_chart_v2`, `derived_lines`, `useful_god_analysis`, `relations`, `judgment_frame`, and `prompt_contract`.

- [ ] **Step 5: Commit verification fixes if needed**

If verification required code changes:

```bash
git add <changed-files>
git commit -m "Fix liuyao v2 verification issues"
```

If no files changed, no commit is needed.
