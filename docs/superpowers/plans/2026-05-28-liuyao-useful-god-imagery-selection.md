# Liuyao Useful-God Imagery Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Liuyao output to v3 with imagery-guided useful-god selection that preserves conflicts using `近取诸身，远取诸象`.

**Architecture:** Add a focused `imagery.py` module for deterministic token-to-six-relative matches and layered useful-god selection. Integrate it in `judgment.py`, keep all v2 fields stable, and update prompt/tests to require the v3 selection fields.

**Tech Stack:** Python 3.11+, pytest, current `dongxuan_agent.liuyao` package.

---

## File Structure

- Create `dongxuan_agent/liuyao/imagery.py`: six-relative imagery dictionary, token matching, useful-god selection.
- Modify `dongxuan_agent/liuyao/judgment.py`: call imagery selection and set schema-related prompt contract updates.
- Modify `dongxuan_agent/liuyao/chart.py`: upgrade schema to `liuyao_chart_v3`.
- Modify `liuyao_prompt.md`: require `useful_god_selection`, layered conflicts, near-self/far-symbol sections.
- Add `tests/test_liuyao_imagery.py`.
- Update existing Liuyao tests from v2 to v3.

---

### Task 1: Imagery Dictionary And Matching

**Files:**
- Create: `tests/test_liuyao_imagery.py`
- Create: `dongxuan_agent/liuyao/imagery.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao.imagery import build_imagery_context


def test_work_offer_contract_matches_official_and_parent_images():
    context = build_imagery_context("问工作 offer 合同什么时候下来", "事业/工作")

    relatives = {match["six_relative"] for match in context["matches"]}
    assert "官鬼" in relatives
    assert "父母" in relatives
    assert "工作" in context["tokens"]
    assert "合同" in context["tokens"]
    assert context["near_self_principle"].startswith("近取诸身")
    assert context["far_symbol_principle"].startswith("远取诸象")
```

- [ ] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_liuyao_imagery.py -v`

Expected: FAIL because `imagery.py` does not exist.

- [ ] **Step 3: Implement imagery context**

Implement:
- `SIX_RELATIVE_IMAGERY`
- deterministic keyword table
- `question_tokens(question)`
- `build_imagery_context(question, domain)`

- [ ] **Step 4: Run test to verify GREEN**

Run: `uv run pytest tests/test_liuyao_imagery.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/imagery.py tests/test_liuyao_imagery.py
git commit -m "Add liuyao imagery matching"
```

---

### Task 2: Useful-God Selection

**Files:**
- Modify: `tests/test_liuyao_imagery.py`
- Modify: `dongxuan_agent/liuyao/imagery.py`

- [ ] **Step 1: Add failing selection tests**

```python
from dongxuan_agent.liuyao import build_liuyao_chart


def test_work_offer_contract_selection_is_layered():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作 offer 合同什么时候下来",
        value="2026-05-28 09:30:00",
    ).to_dict()

    selection = payload["useful_god_selection"]
    assert selection["principle"] == "近取诸身，远取诸象"
    assert selection["selection_result"]["status"] == "layered"
    assert selection["selection_result"]["main_useful_god"] == "官鬼"
    assert "父母" in selection["selection_result"]["auxiliary_useful_gods"]
    assert selection["near_self_focus"][0]["role"] == "世"
    assert {item["six_relative"] for item in selection["far_symbol_focus"]} >= {"官鬼", "父母"}
    assert "不是互斥" in selection["conflicts"][0]["interpretation_hint"]
```

- [ ] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_liuyao_imagery.py -v`

Expected: FAIL because chart output lacks `useful_god_selection`.

- [ ] **Step 3: Implement selection logic**

Implement `build_useful_god_selection(payload, derived_lines, useful_god_analysis, imagery_context)`.

Rules:
- Always include shi line in `near_self_focus`.
- Build `far_symbol_focus` from imagery matches and useful-god matching lines.
- If more than one far-symbol relative is matched, set `status = layered`.
- For work + contract, select `官鬼` as main and `父母` as auxiliary.
- Preserve conflict reading.

- [ ] **Step 4: Run test to verify GREEN**

Run: `uv run pytest tests/test_liuyao_imagery.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/imagery.py tests/test_liuyao_imagery.py
git commit -m "Add liuyao useful god selection"
```

---

### Task 3: Integrate V3 Output

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_session.py`
- Modify: `tests/test_liuyao_judgment.py`

- [ ] **Step 1: Update tests to expect v3 fields**

Update schema assertions to `liuyao_chart_v3`. Add checks for:
- `imagery_context`
- `useful_god_selection`
- prompt contract includes `useful_god_selection`

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py -v`

Expected: FAIL until v3 integration is complete.

- [ ] **Step 3: Integrate v3 in chart/judgment**

Update:
- `schema = liuyao_chart_v3`
- `enrich_payload()` adds `imagery_context` and `useful_god_selection`
- `prompt_contract().must_use_fields` includes `useful_god_selection`

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/chart.py dongxuan_agent/liuyao/judgment.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py
git commit -m "Integrate liuyao v3 useful god selection"
```

---

### Task 4: Prompt Optimization

**Files:**
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Add failing prompt tests**

Add assertions that prompt includes:
- `useful_god_selection`
- `近取诸身`
- `远取诸象`
- `layered`
- `ambiguous`
- instructions not to collapse layered conflicts

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py -v`

Expected: FAIL until prompt is updated.

- [ ] **Step 3: Update prompt**

Update `用神定位` section with:
- near-self focus
- far-symbol focus
- conflicts
- primary axis
- secondary axes
- selection result

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_prompt_policy.py tests/test_liuyao_session.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add liuyao_prompt.md tests/test_liuyao_prompt_policy.py
git commit -m "Optimize liuyao useful god prompt"
```

---

### Task 5: Full Verification

**Files:**
- Modify only files needed for verification fixes.

- [ ] **Step 1: Run Liuyao tests**

Run: `uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v`

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -q`

Expected: PASS.

- [ ] **Step 3: Run boundary scan**

Run: `rg -n "strength_analysis|climate_analysis|pattern_analysis|remedy_analysis|god_candidates|luck_year_remedy|discipline_profile|four_lessons|transmissions|heavenly_officers|day_master_element" dongxuan_agent/liuyao liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py`

Expected: no matches except Liuyao-native `useful_god_candidates` or prompt text forbidding external systems.

- [ ] **Step 4: Run example CLI**

Run: `uv run python -m dongxuan_agent.liuyao_cli --hexagram "离之大有" --question "问工作 offer 合同什么时候下来" --datetime "2026-05-28 09:30:00" --format json`

Expected: JSON includes `schema = liuyao_chart_v3`, `imagery_context`, and `useful_god_selection.selection_result.status = layered`.
