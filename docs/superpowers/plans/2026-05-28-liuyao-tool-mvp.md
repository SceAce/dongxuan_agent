# Liuyao Tool MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent Liuyao chart MVP that accepts manual lines, named hexagrams, and random line generation, then outputs stable JSON and prompt context.

**Architecture:** Add a new `dongxuan_agent.liuyao` package with isolated hexagram, chart, najia, question, and context modules. The package may reuse `dongxuan_agent.calendar_engine.get_calendar_info` for calendar fields only, and must not import Bazi or Daliuren analysis modules.

**Tech Stack:** Python 3.11, dataclasses, argparse, pytest, existing project scripts in `pyproject.toml`.

---

## File Structure

- Create `dongxuan_agent/liuyao/__init__.py`: public Liuyao API exports.
- Create `dongxuan_agent/liuyao/hexagrams.py`: 64 hexagram definitions, aliases, line-state parsing, named-input parsing.
- Create `dongxuan_agent/liuyao/chart.py`: `LiuyaoChart`, calendar serialization, input modes, random generation.
- Create `dongxuan_agent/liuyao/najia.py`: eight-palace metadata, najia branches, six-relative calculation from palace element.
- Create `dongxuan_agent/liuyao/question.py`: question-domain classification and candidate useful gods.
- Create `dongxuan_agent/liuyao/context.py`: chart context JSON builder.
- Create `dongxuan_agent/liuyao_cli.py`: `liuyao-chart` CLI.
- Create `liuyao_prompt.md`: model boundary prompt.
- Create `liuyao_session.py`: prompt plus JSON context output.
- Create `tools_liuyao_chart_wrapper.py`: tool wrapper for chart CLI.
- Create `tools_liuyao_session_wrapper.py`: tool wrapper for session CLI.
- Modify `pyproject.toml`: add `liuyao-chart = "dongxuan_agent.liuyao_cli:main"`.
- Create tests under `tests/test_liuyao_*.py`.

---

### Task 1: Hexagram And Line-State Core

**Files:**
- Create: `tests/test_liuyao_hexagrams.py`
- Create: `dongxuan_agent/liuyao/__init__.py`
- Create: `dongxuan_agent/liuyao/hexagrams.py`

- [ ] **Step 1: Write failing tests**

```python
import pytest

from dongxuan_agent.liuyao.hexagrams import (
    changed_binary,
    hexagram_by_name,
    parse_line_states,
    parse_named_hexagram,
)


def test_manual_line_states_parse_bottom_to_top():
    parsed = parse_line_states("少阳 老阴 少阴 少阳 老阳 少阴")

    assert [line.position for line in parsed] == [1, 2, 3, 4, 5, 6]
    assert "".join(line.yin_yang_binary for line in parsed) == "101110"
    assert [line.position for line in parsed if line.moving] == [2, 5]
    assert changed_binary(parsed) == "111100"


def test_line_state_count_error_mentions_bottom_to_top():
    with pytest.raises(ValueError, match="初爻.*上爻"):
        parse_line_states("少阳 老阴")


def test_line_state_name_error_lists_allowed_states():
    with pytest.raises(ValueError, match="少阳.*老阳.*少阴.*老阴"):
        parse_line_states("少阳 老阴 少阴 少阳 老阳 错误")


def test_hexagram_alias_li_zhi_dayou_derives_second_moving_line():
    parsed = parse_named_hexagram("离之大有")

    assert parsed.original.name == "离为火"
    assert parsed.changed.name == "火天大有"
    assert parsed.moving_lines == [2]
    assert parsed.original.binary_bottom_to_top == "101101"
    assert parsed.changed.binary_bottom_to_top == "111101"


def test_named_hexagram_with_explicit_moving_line_must_be_consistent():
    with pytest.raises(ValueError, match="不一致"):
        parse_named_hexagram("离卦三爻动得大有卦")


def test_unknown_hexagram_name_raises_clear_error():
    with pytest.raises(ValueError, match="未知卦名"):
        hexagram_by_name("不存在")
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_hexagrams.py -v`

Expected: FAIL because `dongxuan_agent.liuyao` is not implemented.

- [ ] **Step 3: Implement core hexagram support**

Implement:
- `LineState`
- `Hexagram`
- `NamedHexagramInput`
- `parse_line_states`
- `changed_binary`
- 64 hexagrams generated from upper/lower trigrams
- aliases for short names such as `离`, `大有`
- named input forms `离之大有`, `离为火之火天大有`, and `离卦二爻动得大有卦`

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_hexagrams.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao tests/test_liuyao_hexagrams.py
git commit -m "Add liuyao hexagram core"
```

---

### Task 2: Palace, Najia, And Six Relatives

**Files:**
- Create: `tests/test_liuyao_najia.py`
- Create: `dongxuan_agent/liuyao/najia.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao.hexagrams import hexagram_by_name
from dongxuan_agent.liuyao.najia import build_najia, palace_info


def test_li_hexagram_palace_shi_ying_and_generation():
    info = palace_info(hexagram_by_name("离为火"))

    assert info["palace"] == "离宫"
    assert info["palace_element"] == "火"
    assert info["generation"] == "本宫卦"
    assert info["shi_position"] == 6
    assert info["ying_position"] == 3


def test_dayou_palace_and_roles_are_available():
    info = palace_info(hexagram_by_name("火天大有"))

    assert info["palace"] == "乾宫"
    assert info["generation"] == "归魂卦"
    assert info["shi_position"] == 3
    assert info["ying_position"] == 6


def test_najia_uses_palace_element_not_day_master():
    payload = build_najia(hexagram_by_name("离为火"))

    assert payload["palace_element"] == "火"
    assert payload["lines"][0]["stem_branch"] == "己卯"
    assert payload["lines"][0]["branch"] == "卯"
    assert payload["lines"][0]["element"] == "木"
    assert payload["lines"][0]["six_relative"] == "父母"
    assert payload["lines"][2]["role"] == "应"
    assert payload["lines"][5]["role"] == "世"
    assert "day_master_element" not in payload
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_najia.py -v`

Expected: FAIL because `dongxuan_agent.liuyao.najia` is not implemented.

- [ ] **Step 3: Implement palace and najia**

Implement a Jing Fang eight-palace table sufficient for all 64 generated hexagrams, including palace name, palace element, generation, shi, and ying. Implement najia stem-branch assignment for eight pure trigrams and derive six relatives from palace element.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_najia.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao/najia.py tests/test_liuyao_najia.py
git commit -m "Add liuyao palace and najia"
```

---

### Task 3: Chart Builder And Context JSON

**Files:**
- Create: `tests/test_liuyao_chart.py`
- Create: `dongxuan_agent/liuyao/chart.py`
- Create: `dongxuan_agent/liuyao/question.py`
- Create: `dongxuan_agent/liuyao/context.py`
- Modify: `dongxuan_agent/liuyao/__init__.py`

- [ ] **Step 1: Write failing tests**

```python
from dongxuan_agent.liuyao import build_liuyao_chart
from dongxuan_agent.liuyao.context import build_liuyao_context


def test_manual_chart_outputs_required_json_without_bazi_or_daliuren_fields():
    chart = build_liuyao_chart(
        lines="少阳 老阴 少阴 少阳 老阳 少阴",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["schema"] == "liuyao_chart_v1"
    assert chart["input"]["method"] == "manual_lines"
    assert chart["input"]["line_order"] == "bottom_to_top"
    assert chart["calendar"]["year_gz"]
    assert chart["calendar"]["month_branch"] == chart["calendar"]["month_gz"][1]
    assert chart["calendar"]["day_branch"] == chart["calendar"]["day_gz"][1]
    assert chart["hexagram"]["moving_lines"] == [2, 5]
    assert chart["lines"][1]["input_state"] == "老阴"
    assert chart["lines"][1]["moving"] is True
    assert chart["question_context"]["domain"] == "事业/工作"
    assert "官鬼" in [item["six_relative"] for item in chart["question_context"]["candidate_useful_gods"]]

    forbidden = {
        "strength_analysis",
        "climate_analysis",
        "pattern_analysis",
        "remedy_analysis",
        "god_candidates",
        "luck_year_remedy",
        "discipline_profile",
        "four_lessons",
        "transmissions",
        "heavenly_officers",
    }
    assert forbidden.isdisjoint(chart)


def test_named_hexagram_chart_preserves_original_changed_and_moving_lines():
    chart = build_liuyao_chart(
        hexagram="离之大有",
        question="问合同",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["input"]["method"] == "named_hexagram"
    assert chart["hexagram"]["original"]["name"] == "离为火"
    assert chart["hexagram"]["changed"]["name"] == "火天大有"
    assert chart["hexagram"]["moving_lines"] == [2]
    assert chart["lines"][1]["moving"] is True


def test_random_chart_accepts_seed_for_repeatable_tests():
    chart = build_liuyao_chart(
        random_lines=True,
        seed=7,
        question="问财运",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert chart["input"]["method"] == "random_lines"
    assert len(chart["lines"]) == 6
    assert {line["input_state"] for line in chart["lines"]} <= {"老阴", "少阳", "少阴", "老阳"}


def test_context_wraps_chart_and_hints():
    payload = build_liuyao_context(
        lines="少阳 老阴 少阴 少阳 老阳 少阴",
        question="问工作",
        value="2026-05-28 09:30:00",
    )

    assert payload["schema"] == "liuyao_chart_v1"
    assert payload["analysis_hints"]["must_check"]
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_chart.py -v`

Expected: FAIL because chart/context builders are not implemented.

- [ ] **Step 3: Implement chart and context builders**

Implement:
- `build_liuyao_chart(lines=None, hexagram=None, random_lines=False, seed=None, question=None, value=None, timezone="Asia/Shanghai")`
- `LiuyaoChart.to_dict()`
- calendar serialization with `month_branch = month_gz[1]`, `day_branch = day_gz[1]`, and `xunkong`
- question classifier for work, money, relationship, exam/study, health, document/contract, and general
- analysis hints without final judgment

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_chart.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add dongxuan_agent/liuyao tests/test_liuyao_chart.py
git commit -m "Build liuyao chart context"
```

---

### Task 4: CLI, Session, Wrappers, Prompt

**Files:**
- Create: `tests/test_liuyao_cli.py`
- Create: `tests/test_liuyao_session.py`
- Create: `dongxuan_agent/liuyao_cli.py`
- Create: `liuyao_prompt.md`
- Create: `liuyao_session.py`
- Create: `tools_liuyao_chart_wrapper.py`
- Create: `tools_liuyao_session_wrapper.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write failing tests**

```python
import json

from dongxuan_agent.liuyao_cli import main as chart_main
from liuyao_session import main as session_main


def _extract_json(output: str) -> dict:
    if "```json" not in output:
        return json.loads(output)
    start = output.index("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_liuyao_cli_outputs_json_for_manual_lines(capsys):
    assert chart_main([
        "--lines",
        "少阳 老阴 少阴 少阳 老阳 少阴",
        "--question",
        "问工作",
        "--datetime",
        "2026-05-28 09:30:00",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["schema"] == "liuyao_chart_v1"
    assert payload["input"]["method"] == "manual_lines"
    assert payload["hexagram"]["moving_lines"] == [2, 5]


def test_liuyao_cli_outputs_json_for_named_hexagram(capsys):
    assert chart_main([
        "--hexagram",
        "离之大有",
        "--question",
        "问合同",
        "--datetime",
        "2026-05-28 09:30:00",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["hexagram"]["original"]["name"] == "离为火"
    assert payload["hexagram"]["changed"]["name"] == "火天大有"


def test_liuyao_session_outputs_prompt_and_json(capsys):
    assert session_main([
        "--hexagram",
        "离之大有",
        "--question",
        "问合同",
        "--datetime",
        "2026-05-28 09:30:00",
        "--include-prompt",
    ]) == 0

    output = capsys.readouterr().out
    payload = _extract_json(output)

    assert "# 六爻分析 Prompt" in output
    assert "## 六爻工具上下文" in output
    assert payload["schema"] == "liuyao_chart_v1"
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: FAIL because CLI/session files are not implemented.

- [ ] **Step 3: Implement CLI, session, wrappers, prompt, and script entry**

Implement CLI modes:

```bash
liuyao-chart --lines "少阳 老阴 少阴 少阳 老阳 少阴" --question "问工作"
liuyao-chart --hexagram "离之大有" --question "问工作"
liuyao-chart --random --question "问工作"
```

Prompt must explicitly forbid Bazi strength/pattern/remedy/luck and Daliuren four lessons/transmissions/heavenly officers/spirit-sha logic.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add pyproject.toml dongxuan_agent/liuyao_cli.py liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py tests/test_liuyao_cli.py tests/test_liuyao_session.py
git commit -m "Add liuyao CLI and session tools"
```

---

### Task 5: Full Verification

**Files:**
- Modify only files needed for fixes found by verification.

- [ ] **Step 1: Run Liuyao test suite**

Run: `uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py -v`

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run: `uv run pytest -q`

Expected: PASS.

- [ ] **Step 3: Run boundary scan**

Run: `rg -n "strength_analysis|climate_analysis|pattern_analysis|remedy_analysis|god_candidates|luck_year_remedy|discipline_profile|four_lessons|transmissions|heavenly_officers|day_master_element" dongxuan_agent/liuyao liuyao_prompt.md liuyao_session.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py`

Expected: no matches except prompt text that explicitly forbids those terms.

- [ ] **Step 4: Commit verification fixes if needed**

If verification required code changes, run:

```bash
git add <changed-files>
git commit -m "Fix liuyao MVP verification issues"
```

If no files changed, no commit is needed.
