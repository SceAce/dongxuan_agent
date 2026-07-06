# Liuyao Spirit Sha Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add v11 auxiliary 神煞 marks for 天乙贵人, 驿马, and 桃花.

**Architecture:** Create `spirit_sha.py` to compute day-stem/day-branch marks and attach matches to derived lines. Wire `spirit_sha_analysis` and `auxiliary_marks` into `judgment.py`, then update schema, layer contract, and prompt.

**Tech Stack:** Python dict modules, pytest, uv.

---

### Task 1: Spirit Sha Module

**Files:**
- Create: `dongxuan_agent/liuyao/spirit_sha.py`
- Create: `tests/test_liuyao_spirit_sha.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`

- [ ] **Step 1:** Write failing test expecting day `壬午` to produce 贵人 `卯/巳`, 驿马 `申`, 桃花 `卯`.
- [ ] **Step 2:** Run focused test and see missing `spirit_sha_analysis`.
- [ ] **Step 3:** Implement marks and line attachment.
- [ ] **Step 4:** Run focused test.
- [ ] **Step 5:** Commit `Add liuyao spirit sha analysis`.

### Task 2: v11 Contract

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `liuyao_prompt.md`
- Modify contract tests.

- [ ] **Step 1:** Update tests for `liuyao_chart_v11`, enabled `spirit_sha`, and prompt auxiliary-only wording.
- [ ] **Step 2:** Run tests and see failures.
- [ ] **Step 3:** Update implementation and prompt.
- [ ] **Step 4:** Run tests and commit `Integrate liuyao v11 spirit sha`.
