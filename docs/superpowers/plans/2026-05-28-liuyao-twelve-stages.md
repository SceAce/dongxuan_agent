# Liuyao Twelve Stages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement v6 十二长生 as a role-aware state modifier in the Liuyao advanced judgment chain.

**Architecture:** Add a focused `twelve_stages.py` module, attach `twelve_stage` to every derived line, add `twelve_stage_analysis`, and enable `twelve_stages` in `advanced_layers` while keeping later layers reserved.

**Tech Stack:** Python 3.13, pytest, existing `dongxuan_agent.liuyao` package.

---

## Task 1: Twelve Stage Module

**Files:**
- Create: `dongxuan_agent/liuyao/twelve_stages.py`
- Test: `tests/test_liuyao_twelve_stages.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao.twelve_stages import twelve_stage


def test_twelve_stage_table_maps_element_and_branch():
    assert twelve_stage("水", "亥")["stage"] == "临官"
    assert twelve_stage("土", "丑")["stage"] == "衰"
    assert twelve_stage("金", "酉")["stage"] == "帝旺"
    assert twelve_stage("水", "亥")["strength_hint"] == "growth"
    assert twelve_stage("金", "酉")["strength_hint"] == "peak"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/test_liuyao_twelve_stages.py -v`

Expected: FAIL with missing module.

- [ ] **Step 3: Implement module**

Create `twelve_stages.py` with stage table, `twelve_stage`, `attach_twelve_stages`, and `build_twelve_stage_analysis`.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/test_liuyao_twelve_stages.py -v`

Expected: PASS.

Commit:

```bash
git add dongxuan_agent/liuyao/twelve_stages.py tests/test_liuyao_twelve_stages.py
git commit -m "Add liuyao twelve stages"
```

## Task 2: v6 Integration

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_judgment.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_session.py`

- [ ] **Step 1: Write failing integration expectations**

Require:

```python
assert payload["schema"] == "liuyao_chart_v6"
assert all("twelve_stage" in line for line in payload["derived_lines"])
assert payload["twelve_stage_analysis"]["enabled"] is True
assert payload["advanced_layers"]["enabled"] == ["spirit_roles", "twelve_stages"]
assert "three_combination" in payload["advanced_layers"]["reserved"]
```

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: FAIL until schema and integration are updated.

- [ ] **Step 3: Implement integration**

Attach twelve stages after spirit roles and before completion chain, then build twelve stage analysis and allow completion chain to include role-aware stage factors.

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_twelve_stages.py -v`

Expected: PASS.

Commit:

```bash
git add dongxuan_agent/liuyao/chart.py dongxuan_agent/liuyao/judgment.py dongxuan_agent/liuyao/spirit_roles.py tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py
git commit -m "Integrate liuyao v6 twelve stages"
```

## Task 3: Prompt and Verification

**Files:**
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Add prompt policy test**

Require prompt text:

```python
def test_liuyao_prompt_requires_role_aware_twelve_stages():
    for text in ["twelve_stage", "twelve_stage_analysis", "十二长生", "状态辅助，不直接定吉凶"]:
        assert text in PROMPT
    assert "十二长生必须先按 spirit_role 解释" in PROMPT
    assert "twelve_stages" in PROMPT
```

- [ ] **Step 2: Run test and verify failure**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py -v`

Expected: FAIL until prompt is updated.

- [ ] **Step 3: Update prompt**

Require role-aware twelve-stage use and continue forbidding disabled later layers.

- [ ] **Step 4: Full verification and commit**

Run:

```bash
uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_templates.py tests/test_liuyao_six_spirits.py tests/test_liuyao_spirit_roles.py tests/test_liuyao_twelve_stages.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v
uv run pytest -q
```

Commit:

```bash
git add liuyao_prompt.md tests/test_liuyao_prompt_policy.py
git commit -m "Optimize liuyao v6 prompt policy"
```
