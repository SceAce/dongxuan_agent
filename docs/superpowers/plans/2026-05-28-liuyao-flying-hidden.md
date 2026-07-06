# Liuyao Flying Hidden Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add v8 飞伏 support so missing six-relative images are emitted deterministically and can feed the completion chain.

**Architecture:** Extend `najia.py` so each chart computes hidden spirits from its palace pure hexagram. Add a focused `flying_hidden.py` module that interprets these hidden spirits through the existing spirit-role chain and exposes completion factors. Wire the module into `judgment.py`, `spirit_roles.py`, chart schema, tests, and prompt policy.

**Tech Stack:** Python dataclasses/dicts, existing Liuyao modules, pytest, uv.

---

### Task 1: Najia Hidden Spirits

**Files:**
- Modify: `dongxuan_agent/liuyao/najia.py`
- Modify: `tests/test_liuyao_najia.py`

- [ ] **Step 1: Write the failing test**

Add this test to `tests/test_liuyao_najia.py`:

```python
def test_missing_relative_gets_hidden_spirit_from_palace_pure_hexagram():
    payload = build_najia(hexagram_by_name("天地否"))

    assert payload["missing_relatives"] == ["子孙"]
    hidden = payload["hidden_spirits"]

    assert hidden == [
        {
            "position": 1,
            "name": "初爻",
            "hidden_stem_branch": "甲子",
            "hidden_branch": "子",
            "hidden_element": "水",
            "hidden_six_relative": "子孙",
            "flying_stem_branch": "乙未",
            "flying_branch": "未",
            "flying_element": "土",
            "flying_six_relative": "父母",
            "source_palace_hexagram": "乾为天",
        }
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_liuyao_najia.py::test_missing_relative_gets_hidden_spirit_from_palace_pure_hexagram -v`

Expected: FAIL because `hidden_spirits` is still empty.

- [ ] **Step 3: Implement hidden-spirit generation**

In `dongxuan_agent/liuyao/najia.py`, add helpers:

```python
def _hidden_spirits(hexagram: Hexagram, visible_lines: list[dict], missing_relatives: list[str], palace: dict) -> list[dict]:
    if not missing_relatives:
        return []
    palace_trigram = palace["palace"].replace("宫", "")
    pure_hexagram = _hexagram_by_short_name(palace_trigram)
    pure_lower = NAJIA_BY_TRIGRAM[pure_hexagram.lower_trigram]["lower"]
    pure_upper = NAJIA_BY_TRIGRAM[pure_hexagram.upper_trigram]["upper"]
    pure_stem_branches = pure_lower + pure_upper
    visible_by_position = {line["position"]: line for line in visible_lines}
    result = []
    for position, stem_branch in enumerate(pure_stem_branches, start=1):
        branch = stem_branch[1]
        hidden_element = BRANCH_ELEMENTS[branch]
        hidden_relative = six_relative(palace["palace_element"], hidden_element)
        if hidden_relative not in missing_relatives:
            continue
        flying = visible_by_position[position]
        result.append(
            {
                "position": position,
                "name": _line_name(position),
                "hidden_stem_branch": stem_branch,
                "hidden_branch": branch,
                "hidden_element": hidden_element,
                "hidden_six_relative": hidden_relative,
                "flying_stem_branch": flying["stem_branch"],
                "flying_branch": flying["branch"],
                "flying_element": flying["element"],
                "flying_six_relative": flying["six_relative"],
                "source_palace_hexagram": pure_hexagram.name,
            }
        )
    return result
```

Then call it from `build_najia()` after `missing_relatives` is computed.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_liuyao_najia.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/najia.py tests/test_liuyao_najia.py
git commit -m "Add liuyao hidden spirit mapping"
```

### Task 2: Flying Hidden Analysis

**Files:**
- Create: `dongxuan_agent/liuyao/flying_hidden.py`
- Create: `tests/test_liuyao_flying_hidden.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_liuyao_flying_hidden.py`:

```python
from dongxuan_agent.liuyao import build_liuyao_chart


def test_hidden_useful_god_is_analyzed_when_main_relative_is_missing():
    payload = build_liuyao_chart(
        hexagram="否之观",
        question="问孩子考试是否顺利",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["flying_hidden_analysis"]

    assert analysis["enabled"] is True
    assert analysis["hidden_useful_gods"]
    hidden = analysis["hidden_useful_gods"][0]
    assert hidden["hidden_six_relative"] == "子孙"
    assert hidden["position"] == 1
    assert hidden["hidden_role_impact"] == "supports_useful_god"
    assert hidden["flying_controls_hidden"] is True
    assert any(item["type"] == "hidden_useful_god_controlled_by_flying" for item in payload["completion_chain"]["blocking_factors"])
    assert not any("飞伏未实现" in item for item in payload["completion_chain"]["unresolved"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_liuyao_flying_hidden.py -v`

Expected: FAIL because `flying_hidden_analysis` does not exist.

- [ ] **Step 3: Implement flying hidden analysis**

Add `dongxuan_agent/liuyao/flying_hidden.py` with:

```python
from __future__ import annotations

from .relations import element_relation


def attach_hidden_spirits(derived_lines: list[dict], hidden_spirits: list[dict]) -> None:
    by_position: dict[int, list[dict]] = {}
    for hidden in hidden_spirits:
        by_position.setdefault(hidden["position"], []).append(hidden)
    for line in derived_lines:
        line["hidden_spirits"] = list(by_position.get(line["position"], []))


def build_flying_hidden_analysis(hidden_spirits: list[dict], spirit_role_analysis: dict) -> dict:
    hidden_lines = []
    hidden_useful_gods = []
    relations = []
    unresolved = []
    for hidden in hidden_spirits:
        item = {**hidden}
        item["hidden_role_impact"] = _role_impact(hidden["hidden_element"], spirit_role_analysis)
        item["flying_to_hidden_relation"] = element_relation(hidden["flying_element"], hidden["hidden_element"])
        item["hidden_to_flying_relation"] = element_relation(hidden["hidden_element"], hidden["flying_element"])
        item["flying_generates_hidden"] = item["flying_to_hidden_relation"] in {"generates", "same"}
        item["flying_controls_hidden"] = item["flying_to_hidden_relation"] == "controls"
        item["hidden_controls_flying"] = item["hidden_to_flying_relation"] == "controls"
        item["reason"] = _reason(item)
        hidden_lines.append(item)
        if item["hidden_role_impact"] in {"supports_useful_god", "supports_original_spirit"}:
            hidden_useful_gods.append(item)
        relations.append(_relation_summary(item))
    if spirit_role_analysis["status"] != "ready":
        unresolved.append("主用神链未定，飞伏只列伏神不作角色裁决。")
    return {
        "enabled": True,
        "scope": "飞伏只补缺失六亲与隐藏用神，不替代上卦用神和动变主线。",
        "hidden_lines": hidden_lines,
        "hidden_useful_gods": hidden_useful_gods,
        "relations": relations,
        "unresolved": unresolved,
    }


def completion_factors(flying_hidden_analysis: dict) -> dict:
    supporting = []
    blocking = []
    mixed = []
    for item in flying_hidden_analysis["hidden_lines"]:
        factor = {
            "line": item["position"],
            "hidden_six_relative": item["hidden_six_relative"],
            "hidden_element": item["hidden_element"],
            "flying_six_relative": item["flying_six_relative"],
            "flying_element": item["flying_element"],
            "summary": item["reason"],
        }
        if item["hidden_role_impact"] in {"supports_useful_god", "supports_original_spirit"}:
            if item["flying_generates_hidden"]:
                supporting.append({**factor, "type": f"hidden_{_role_key(item)}_supported_by_flying"})
            elif item["flying_controls_hidden"]:
                blocking.append({**factor, "type": f"hidden_{_role_key(item)}_controlled_by_flying"})
            else:
                mixed.append({**factor, "type": f"hidden_{_role_key(item)}_present_but_buried"})
        elif item["hidden_role_impact"] in {"supports_avoiding_spirit", "supports_enemy_spirit"}:
            blocking.append({**factor, "type": f"hidden_{_role_key(item)}_supported"})
        else:
            mixed.append({**factor, "type": "hidden_role_unresolved"})
    return {"supporting_factors": supporting, "blocking_factors": blocking, "mixed_factors": mixed}
```

Wire it in `judgment.enrich_payload()` before completion-chain construction, and pass its completion factors to `build_completion_chain()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_liuyao_flying_hidden.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/flying_hidden.py dongxuan_agent/liuyao/judgment.py dongxuan_agent/liuyao/spirit_roles.py tests/test_liuyao_flying_hidden.py
git commit -m "Add liuyao flying hidden analysis"
```

### Task 3: v8 Payload And Prompt Contract

**Files:**
- Modify: `dongxuan_agent/liuyao/chart.py`
- Modify: `dongxuan_agent/liuyao/judgment.py`
- Modify: `dongxuan_agent/liuyao/spirit_roles.py`
- Modify: `liuyao_prompt.md`
- Modify: `tests/test_liuyao_chart.py`
- Modify: `tests/test_liuyao_cli.py`
- Modify: `tests/test_liuyao_judgment.py`
- Modify: `tests/test_liuyao_session.py`
- Modify: `tests/test_liuyao_prompt_policy.py`

- [ ] **Step 1: Write failing contract tests**

Update existing schema assertions from `liuyao_chart_v7` to `liuyao_chart_v8`, assert `flying_hidden_analysis` is in payload and `prompt_contract.must_use_fields`, and add a prompt-policy test:

```python
def test_liuyao_prompt_requires_bounded_flying_hidden():
    for text in ["flying_hidden_analysis", "飞伏", "不得编造伏神", "najia.hidden_spirits"]:
        assert text in PROMPT
    assert "不得输出具体应期" in PROMPT
```

- [ ] **Step 2: Run contract tests to verify failure**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -q`

Expected: FAIL because schema/prompt contract is still v7.

- [ ] **Step 3: Implement contract and prompt changes**

Change:

- `chart.py` schema to `liuyao_chart_v8`;
- `advanced_layers.enabled` to include `flying_hidden`;
- `advanced_layers.reserved` to remove `flying_hidden`;
- `prompt_contract.must_use_fields` to include `flying_hidden_analysis`;
- `prompt_contract.must_not_infer` to remove "未实现的飞伏" and keep timing/spirit-sha restrictions;
- `liuyao_prompt.md` to require bounded use of `flying_hidden_analysis` and forbid invented hidden spirits.

- [ ] **Step 4: Run contract tests**

Run: `uv run pytest tests/test_liuyao_chart.py tests/test_liuyao_judgment.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py tests/test_liuyao_flying_hidden.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/liuyao/chart.py dongxuan_agent/liuyao/judgment.py dongxuan_agent/liuyao/spirit_roles.py liuyao_prompt.md tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_judgment.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py tests/test_liuyao_flying_hidden.py
git commit -m "Integrate liuyao v8 flying hidden"
```

### Task 4: Verification

**Files:**
- Read only.

- [ ] **Step 1: Run Liuyao suite**

Run:

```bash
uv run pytest tests/test_liuyao_hexagrams.py tests/test_liuyao_najia.py tests/test_liuyao_strength.py tests/test_liuyao_judgment.py tests/test_liuyao_imagery.py tests/test_liuyao_templates.py tests/test_liuyao_six_spirits.py tests/test_liuyao_spirit_roles.py tests/test_liuyao_twelve_stages.py tests/test_liuyao_combinations.py tests/test_liuyao_flying_hidden.py tests/test_liuyao_chart.py tests/test_liuyao_cli.py tests/test_liuyao_session.py tests/test_liuyao_prompt_policy.py -v
```

Expected: PASS.

- [ ] **Step 2: Run full suite**

Run: `uv run pytest -q`

Expected: PASS.

- [ ] **Step 3: Scan Liuyao boundary**

Run:

```bash
rg -n "day_master_element|four_lessons|transmissions|heavenly_officers|大六壬四课|八字旺衰|未实现的飞伏" dongxuan_agent/liuyao liuyao_prompt.md tests/test_liuyao_*.py
```

Expected: no Bazi/Daliuren field usage inside Liuyao, and no stale "未实现的飞伏" prompt contract after v8.

- [ ] **Step 4: Commit verification docs only if changed**

No commit is needed unless verification changes files.
