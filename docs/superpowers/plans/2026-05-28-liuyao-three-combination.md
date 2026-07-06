# Liuyao Three Combination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement v7 三合/半合/待合 as role-aware combination evidence.

**Architecture:** Add `combinations.py` to detect branch groups and role impact. Wire `combination_analysis` into judgment, enable `three_combination`, and feed role-aware combination factors into `completion_chain`.

**Tech Stack:** Python 3.13, pytest, existing `dongxuan_agent.liuyao` package.

---

## Task 1: Combination Module

**Files:**
- Create: `dongxuan_agent/liuyao/combinations.py`
- Test: `tests/test_liuyao_combinations.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao import build_liuyao_chart


def test_li_dayou_detects_si_you_half_combination_supporting_original_spirit():
    payload = build_liuyao_chart(hexagram="离之大有", question="问工作 offer 合同什么时候下来", value="2026-05-28 09:30:00").to_dict()

    analysis = payload["combination_analysis"]
    assert analysis["enabled"] is True
    group = next(item for item in analysis["groups"] if item["element"] == "金" and set(item["branches"]) >= {"巳", "酉"})

    assert group["type"] == "half_combination"
    assert group["role_impact"] == "supports_original_spirit"
    assert set(group["line_positions"]) >= {4, 6}
```

- [ ] **Step 2: Run and verify failure**

Run: `uv run pytest tests/test_liuyao_combinations.py -v`

Expected: FAIL because `combination_analysis` does not exist.

- [ ] **Step 3: Implement module and integration**

Create `combinations.py` with `build_combination_analysis`. Integrate after `twelve_stage_analysis`.

- [ ] **Step 4: Run and commit**

Run: `uv run pytest tests/test_liuyao_combinations.py -v`

Expected: PASS.

Commit:

```bash
git add dongxuan_agent/liuyao/combinations.py dongxuan_agent/liuyao/judgment.py tests/test_liuyao_combinations.py
git commit -m "Add liuyao three combination analysis"
```

## Task 2: v7 Contract and Prompt

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_judgment.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_session.py`
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Update tests**

Require:

```python
assert payload["schema"] == "liuyao_chart_v7"
assert payload["advanced_layers"]["enabled"] == ["spirit_roles", "twelve_stages", "three_combination"]
assert payload["combination_analysis"]["enabled"] is True
```

Prompt requires:

```python
assert "combination_analysis" in PROMPT
assert "三合必须按 role_impact 解释" in PROMPT
assert "不得单凭三合断吉凶" in PROMPT
```

- [ ] **Step 2: Implement updates**

Upgrade schema, advanced layers, prompt, and completion-chain integration.

- [ ] **Step 3: Full verification and commit**

Run:

```bash
uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_templates.py tests/test_liuyao_six_spirits.py tests/test_liuyao_spirit_roles.py tests/test_liuyao_twelve_stages.py tests/test_liuyao_combinations.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v
uv run pytest -q
```

Commit:

```bash
git add dongxuan_agent/liuyao/chart.py dongxuan_agent/liuyao/spirit_roles.py liuyao_prompt.md tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py
git commit -m "Integrate liuyao v7 three combination"
```
