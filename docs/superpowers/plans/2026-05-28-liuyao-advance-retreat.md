# Liuyao Advance Retreat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add v9 进退神 support for moving lines and feed role-aware trend factors into completion-chain synthesis.

**Architecture:** Create a focused `advance_retreat.py` module that consumes `derived_lines` after `spirit_role` and existing changed-line data from `relations.moving_effects`. Wire its analysis and completion factors into `judgment.py`, update `advanced_layers`, schema, prompt contract, and tests.

**Tech Stack:** Python dict modules, pytest, uv.

---

### Task 1: Analysis Module

**Files:**
- Create: `dongxuan_agent/liuyao/advance_retreat.py`
- Create: `tests/test_liuyao_advance_retreat.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`

- [ ] **Step 1: Write failing tests**

Create tests that verify `申 -> 酉` is advance and, when the line is 原神, produces `support_increases`.

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/test_liuyao_advance_retreat.py -v`

Expected: FAIL because `advance_retreat_analysis` is missing.

- [ ] **Step 3: Implement module and completion factors**

Implement same-element branch pairs only:

```python
ADVANCE_PAIRS = {("寅", "卯"), ("巳", "午"), ("申", "酉"), ("亥", "子")}
RETREAT_PAIRS = {(right, left) for left, right in ADVANCE_PAIRS}
```

Map role impact by `spirit_role` and place completion factors accordingly.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_liuyao_advance_retreat.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/advance_retreat.py dongxuan_agent/liuyao/judgment.py dongxuan_agent/liuyao/spirit_roles.py tests/test_liuyao_advance_retreat.py
git commit -m "Add liuyao advance retreat analysis"
```

### Task 2: v9 Contract

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `liuyao_prompt.md`
- Modify existing Liuyao contract tests.

- [ ] **Step 1: Update failing contract tests**

Assert schema `liuyao_chart_v9`, enabled `advance_retreat`, payload field `advance_retreat_analysis`, and prompt bounded 进退 wording.

- [ ] **Step 2: Run tests to verify failure**

Run contract test subset.

- [ ] **Step 3: Implement schema, prompt, and contract changes**

Remove `advance_retreat` from reserved layers and add `advance_retreat_analysis` to must-use fields.

- [ ] **Step 4: Verify and commit**

Run focused contract tests, then commit with `Integrate liuyao v9 advance retreat`.
