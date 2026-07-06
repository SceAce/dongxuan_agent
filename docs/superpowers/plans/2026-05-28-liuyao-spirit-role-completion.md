# Liuyao Spirit Role Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement v5 原忌仇用闲神, completion-chain evidence, and `advanced_layers` while keeping later rules reserved.

**Architecture:** Add a focused `spirit_roles.py` module for role derivation and completion-chain synthesis. Wire it into `judgment.enrich_payload`, upgrade chart schema to `liuyao_chart_v5`, and update prompt policy to use only enabled advanced layers.

**Tech Stack:** Python 3.13, pytest, existing `dongxuan_agent.liuyao` package.

---

## File Structure

- Create `dongxuan_agent/liuyao/spirit_roles.py`: 原忌仇用闲神 role derivation and completion-chain synthesis.
- Modify `dongxuan_agent/liuyao/judgment.py`: attach role metadata, add `spirit_role_analysis`, `completion_chain`, and `advanced_layers`.
- Modify `dongxuan_agent/liuyao/chart.py`: upgrade schema to `liuyao_chart_v5`.
- Modify `liuyao_prompt.md`: require role-chain evidence and reserve later advanced layers.
- Add/modify tests under `tests/`.

## Task 1: Spirit Role Module

**Files:**
- Create: `dongxuan_agent/liuyao/spirit_roles.py`
- Test: `tests/test_liuyao_spirit_roles.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao import build_liuyao_chart


def test_work_offer_derives_spirit_roles_from_main_useful_god():
    payload = build_liuyao_chart(hexagram="离之大有", question="问工作 offer 合同什么时候下来", value="2026-05-28 09:30:00").to_dict()

    analysis = payload["spirit_role_analysis"]

    assert analysis["status"] == "ready"
    assert analysis["main_useful_god"] == "官鬼"
    assert analysis["useful_god_elements"] == ["水"]
    assert analysis["role_elements"]["original_spirit"] == ["金"]
    assert analysis["role_elements"]["avoiding_spirit"] == ["土"]
    assert analysis["role_elements"]["enemy_spirit"] == ["火"]

    roles = {line["position"]: line["role"] for line in analysis["by_line"]}
    assert roles[3] == "useful_god"
    assert roles[2] == "avoiding_spirit"
    assert roles[4] == "original_spirit"
    assert roles[6] == "enemy_spirit"


def test_completion_chain_marks_moving_avoiding_spirit_as_blocking():
    payload = build_liuyao_chart(hexagram="离之大有", question="问工作 offer 合同什么时候下来", value="2026-05-28 09:30:00").to_dict()

    chain = payload["completion_chain"]

    assert chain["mode"] == "spirit_role_completion"
    assert chain["tendency"] in {"blocked", "mixed"}
    assert chain["tendency"] != "supported"
    assert any(item["type"] == "useful_god_present" and item["line"] == 3 for item in chain["supporting_factors"])
    assert any(item["type"] == "avoiding_spirit_moving_controls_useful_god" and item["line"] == 2 and item["target_line"] == 3 for item in chain["blocking_factors"])
    assert any(item["type"] == "layered_auxiliary" for item in chain["mixed_factors"])
```

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/test_liuyao_spirit_roles.py -v`

Expected: FAIL because `spirit_role_analysis` and `completion_chain` do not exist.

- [ ] **Step 3: Implement module and integration**

Create `spirit_roles.py` with `build_spirit_role_analysis`, `build_completion_chain`, and `advanced_layers`.

Wire in `judgment.enrich_payload` after `useful_god_selection` and before `relations`.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/test_liuyao_spirit_roles.py -v`

Expected: PASS.

Commit:

```bash
git add dongxuan_agent/liuyao/spirit_roles.py dongxuan_agent/liuyao/judgment.py tests/test_liuyao_spirit_roles.py
git commit -m "Add liuyao spirit role completion"
```

## Task 2: v5 Payload Contract

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_judgment.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_session.py`

- [ ] **Step 1: Update tests for v5 schema and fields**

Require:

```python
assert payload["schema"] == "liuyao_chart_v5"
assert "spirit_role_analysis" in payload
assert "completion_chain" in payload
assert payload["advanced_layers"]["enabled"] == ["spirit_roles"]
assert "timing" in payload["advanced_layers"]["reserved"]
assert all("spirit_role" in line and "spirit_role_reason" in line for line in payload["derived_lines"])
```

- [ ] **Step 2: Verify tests fail**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: FAIL until schema and assertions are updated.

- [ ] **Step 3: Upgrade schema to v5 and align tests**

Change `chart.py` schema to `liuyao_chart_v5`, then update old v4 assertions.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: PASS.

Commit:

```bash
git add dongxuan_agent/liuyao/chart.py tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py
git commit -m "Integrate liuyao v5 payload contract"
```

## Task 3: Prompt Policy and Verification

**Files:**
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Add prompt policy tests**

Require prompt text:

```python
def test_liuyao_prompt_requires_spirit_roles_and_advanced_layer_order():
    for text in ["spirit_role_analysis", "completion_chain", "advanced_layers", "原神", "忌神", "仇神", "闲神"]:
        assert text in PROMPT
    assert "先看用神，再看原神，再看忌神，再看仇神" in PROMPT
    assert "动爻必须先按 spirit_role 判断" in PROMPT
    assert "只有 advanced_layers.enabled 中的层可以作为证据" in PROMPT
    assert "不得输出具体应期" in PROMPT
```

- [ ] **Step 2: Verify test fails**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py -v`

Expected: FAIL until prompt is updated.

- [ ] **Step 3: Update prompt**

Add role-chain and advanced-layer rules:

- Use `spirit_role_analysis` after `useful_god_selection`.
- Use `completion_chain` as success/blockage evidence.
- Moving lines must be interpreted by `spirit_role` before six-spirit imagery.
- Only `advanced_layers.enabled` layers can be evidence.
- Do not output timing while `timing` is reserved.

- [ ] **Step 4: Full verification and commit**

Run:

```bash
uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_templates.py tests/test_liuyao_six_spirits.py tests/test_liuyao_spirit_roles.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v
uv run pytest -q
rg -n "strength_analysis|climate_analysis|pattern_analysis|remedy_analysis|god_candidates|luck_year_remedy|discipline_profile|four_lessons|transmissions|heavenly_officers|day_master_element" dongxuan_agent/liuyao liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py
uv run python -m dongxuan_agent.liuyao_cli --hexagram "离之大有" --question "问工作 offer 合同什么时候下来" --datetime "2026-05-28 09:30:00" --format json
```

Expected: all tests pass; boundary scan has no problematic matches; CLI emits v5 and spirit-role fields.

Commit:

```bash
git add liuyao_prompt.md tests/test_liuyao_prompt_policy.py
git commit -m "Optimize liuyao v5 prompt policy"
```
