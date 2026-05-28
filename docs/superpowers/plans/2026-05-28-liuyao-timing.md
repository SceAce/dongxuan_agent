# Liuyao Timing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add v10 应期 candidate generation while keeping outputs branch-based and non-date-specific.

**Architecture:** Create `timing.py` to collect bounded branch trigger candidates from existing layers. Wire `timing_analysis` into `judgment.py`, add the layer to `advanced_layers`, update schema and prompt contract.

**Tech Stack:** Python dict modules, pytest, uv.

---

### Task 1: Timing Candidate Module

**Files:**
- Create: `dongxuan_agent/liuyao/timing.py`
- Create: `tests/test_liuyao_timing.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`

- [ ] **Step 1:** Write failing test for `晋之大有` expecting an `advance_retreat_value` candidate branch `午`.
- [ ] **Step 2:** Run `uv run pytest tests/test_liuyao_timing.py -v`, expect missing `timing_analysis`.
- [ ] **Step 3:** Implement candidate collection and dedupe.
- [ ] **Step 4:** Run focused tests, expect PASS.
- [ ] **Step 5:** Commit `Add liuyao timing candidates`.

### Task 2: v10 Contract

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `liuyao_prompt.md`
- Modify existing contract tests.

- [ ] **Step 1:** Update tests to expect `liuyao_chart_v10`, enabled `timing`, and bounded prompt wording.
- [ ] **Step 2:** Run tests and see failures.
- [ ] **Step 3:** Update contract and prompt.
- [ ] **Step 4:** Run tests and commit `Integrate liuyao v10 timing`.
