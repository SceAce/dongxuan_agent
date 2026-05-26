# Bazi Year Event Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structured 八字年份事件推断中间层 that explains what a target year is likely to activate, with evidence, conflicts, and issue-domain candidates, without performing final free-form fortune telling in code.

**Architecture:** Keep 八字排盘 and analysis separate. `bazi.py` remains the chart extractor; new modules derive analysis hints from chart JSON, rule cards, 大运, 流年干支, 十神, 宫位, and 地支关系. Prompt/session layers consume the hints and require model output to synthesize one main image and at most one secondary image.

**Tech Stack:** Python 3.14 via `uv`, `sxtwl`, pytest, existing `dongxuan_agent` package, local tools in `/home/source/Documents/东玄知识库/tools`.

---

## File Structure

- Create `dongxuan_agent/bazi_analysis.py`: deterministic analysis-hints engine for target year, current luck, flow-year ten gods, activated palaces, relations, and event candidates.
- Create `dongxuan_agent/bazi_rule_cards.py`: 八字-specific source-backed rule cards for ten gods, palaces, yearly activation, luck/year interactions, and event domains.
- Create `bazi_session.py`: session script that emits 八字 Prompt plus chart JSON plus `analysis_hints` and `rule_cards`.
- Create `bazi_prompt.md`: strict analysis Prompt for 八字, mirroring the 大六壬 workflow but focused on original chart, luck, target year, and event synthesis.
- Create `tools_bazi_session_wrapper.py`: wrapper for `/home/source/Documents/东玄知识库/tools/bazi_session.py`.
- Modify `dongxuan_agent/bazi.py`: expose helper fields needed by analysis, if tests reveal gaps.
- Modify `dongxuan_agent/bazi_cli.py`: no analysis output here unless explicitly requested; keep chart CLI focused.
- Modify `pyproject.toml`: add `bazi-session = "bazi_session:main"` only if import layout supports it; otherwise keep the root script only.
- Add tests:
  - `tests/test_bazi_analysis.py`
  - `tests/test_bazi_rule_cards.py`
  - `tests/test_bazi_session.py`
  - update `tests/test_bazi.py` only for chart field compatibility.

## Domain Rules For V1

V1 must support these event domains:

- 学业/考试/证书: 印、食伤、官杀、月柱、父母/文书象、当前大运与流年是否引动印官食伤。
- 事业/规则压力: 官杀、印、月柱、流年官杀、大运官杀、官印组合、伤官见官冲突。
- 财务/资源: 财星、比劫、食伤生财、财被冲合、男命感情资源兼象但不能直接断感情。
- 感情/关系: 男命看财星、女命看官杀、日支夫妻宫、合冲刑害、桃花后续可扩展。
- 家庭/长辈: 年柱、月柱、印星、年/月柱被冲合刑害。
- 健康/压力: 官杀过重、刑冲、日主受克泄耗、白虎病符类暂不做八字内置神煞。
- 迁移变化: 冲动日支/月支/年支、驿马后续可扩展、大运流年引动。
- 人际竞争: 比劫、劫财透、比劫夺财、月柱同辈环境。

V1 must not decide final 身强身弱、格局、用神。 It may output `strength_evidence` and `structure_conflicts` only.

---

### Task 1: Add 八字 Rule Cards

**Files:**
- Create: `dongxuan_agent/bazi_rule_cards.py`
- Test: `tests/test_bazi_rule_cards.py`

- [ ] **Step 1: Write failing tests for rule cards**

Create `tests/test_bazi_rule_cards.py`:

```python
from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context


def test_bazi_rule_context_returns_general_and_year_event_cards():
    context = build_bazi_rule_context(question="推断2025年发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}

    assert context["mode"] == "year_event"
    assert "原局结构优先" in names
    assert "流年引动" in names
    assert "大运流年合参" in names
    assert all(card["use_when"] for card in context["cards"])
    assert all(card["avoid"] for card in context["cards"])
    assert all(card["sources"] for card in context["cards"])


def test_bazi_rule_context_includes_event_domain_cards():
    context = build_bazi_rule_context(question="2025年学业和感情发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}

    assert "学业/考试取象" in names
    assert "感情/关系取象" in names
    assert "财务/资源取象" in names
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run python -m pytest tests/test_bazi_rule_cards.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'dongxuan_agent.bazi_rule_cards'`.

- [ ] **Step 3: Implement minimal rule cards**

Create `dongxuan_agent/bazi_rule_cards.py`:

```python
from __future__ import annotations


GENERAL_CARDS = (
    {
        "name": "原局结构优先",
        "meaning": "先看原局四柱、日主、月令、十神、藏干、地支关系，再看大运流年引动。",
        "use_when": ["所有八字分析"],
        "avoid": "不可只凭单个流年干支或单个十神直接断具体事件。",
        "sources": ["八字规则 V1：由本地八字资料与项目排盘字段整理"],
        "implemented": True,
    },
    {
        "name": "流年引动",
        "meaning": "流年通过天干十神、地支冲合刑害、伏吟并临来引动原局宫位和十神。",
        "use_when": ["用户询问某一年发生什么", "用户询问某年趋势"],
        "avoid": "流年只说明触发点，不等于事件已经发生；必须合大运和原局。",
        "sources": ["八字规则 V1：大运流年合参"],
        "implemented": True,
    },
    {
        "name": "大运流年合参",
        "meaning": "大运提供十年背景，流年提供当年触发；流年落在大运主题内时事件更明显。",
        "use_when": ["所有带 target_year 的分析"],
        "avoid": "不可脱离大运只看流年，也不可脱离原局只看大运。",
        "sources": ["八字规则 V1：运年命三层合参"],
        "implemented": True,
    },
)


DOMAIN_CARDS = {
    "学业": {
        "name": "学业/考试取象",
        "meaning": "学业考试重点看印、食伤、官杀、月柱和文书规则压力。",
        "use_when": ["问题包含学业、考试、证书、申请、竞赛"],
        "avoid": "印星或官星出现不等于必过，须看冲合刑害和大运流年是否同向。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
    "感情": {
        "name": "感情/关系取象",
        "meaning": "男命以财星为重要关系象，女命以官杀为重要关系象，同时看日支夫妻宫。",
        "use_when": ["问题包含感情、恋爱、对象、关系、婚姻"],
        "avoid": "财星或官杀被引动不能直接断恋爱或结婚，必须合日支和现实背景。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
    "财": {
        "name": "财务/资源取象",
        "meaning": "财务资源看财星、比劫、食伤生财、财被冲合和财星是否透出。",
        "use_when": ["问题包含财、钱、资源、收入、投资"],
        "avoid": "财星出现不等于得财，比劫旺或冲破时可能是消耗竞争。",
        "sources": ["八字事件取象 V1"],
        "implemented": True,
    },
}


def build_bazi_rule_context(question: str | None = None, target_year: int | None = None) -> dict:
    question = question or ""
    cards = list(GENERAL_CARDS)
    for keyword, card in DOMAIN_CARDS.items():
        if keyword in question:
            cards.append(card)
    if target_year is not None and not any(card["name"] == "学业/考试取象" for card in cards):
        cards.extend([DOMAIN_CARDS["学业"], DOMAIN_CARDS["财"]])
    return {
        "mode": "year_event" if target_year is not None else "chart_structure",
        "target_year": target_year,
        "selection_rule": "规则卡片只提供取象边界；最终结论必须回指 analysis_hints 与命盘字段。",
        "cards": cards,
    }
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
uv run python -m pytest tests/test_bazi_rule_cards.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/bazi_rule_cards.py tests/test_bazi_rule_cards.py
git commit -m "Add bazi analysis rule cards"
```

---

### Task 2: Add Year Event Analysis Hints Engine

**Files:**
- Create: `dongxuan_agent/bazi_analysis.py`
- Test: `tests/test_bazi_analysis.py`

- [ ] **Step 1: Write failing tests for target year hints**

Create `tests/test_bazi_analysis.py`:

```python
from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints


def test_year_analysis_hints_for_2006_birth_target_2025():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    hints = build_year_analysis_hints(chart, target_year=2025)

    assert hints["target_year"] == 2025
    assert hints["year_ganzhi"] == "乙巳"
    assert hints["current_luck"]["ganzhi"] == "壬寅"
    assert hints["flow_year"]["stem_ten_god"] == "偏财"
    assert {"stem": "丙", "ten_god": "正官"} in hints["flow_year"]["hidden_stems"]
    assert any(item["field"] == "流年支与日支" and item["type"] == "并临" for item in hints["activated_relations"])
    assert any(item["domain"] == "学业/考试/规则压力" for item in hints["event_candidates"])
    assert any(item["domain"] == "财务/资源/男命关系议题" for item in hints["event_candidates"])


def test_year_analysis_hints_marks_conflicts():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    hints = build_year_analysis_hints(chart, target_year=2025)

    assert hints["conflicts"]
    assert all(item["evidence"] for item in hints["event_candidates"])
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run python -m pytest tests/test_bazi_analysis.py -q
```

Expected: FAIL with missing module.

- [ ] **Step 3: Implement `bazi_analysis.py`**

Create `dongxuan_agent/bazi_analysis.py`:

```python
from __future__ import annotations

from .bazi import BaziChart, HIDDEN_STEMS, ten_god
from .constants import BRANCH_OPPOSITE, BRANCH_PUNISH, BRANCHES, JIAZI
from .divination import year_ganzhi


def build_year_analysis_hints(chart: BaziChart, target_year: int) -> dict:
    payload = chart.to_dict()
    year_gz = year_ganzhi(target_year)
    day_master = payload["day_master"]
    flow_branch = year_gz[1]
    luck = _current_luck(payload.get("luck"), target_year, payload["calendar"]["datetime"][:4])
    relations = _relations_with_chart(payload["pillars"], flow_branch)
    if luck:
        relations.extend(_relations_with_luck(luck["ganzhi"][1], flow_branch))
    candidates = _event_candidates(day_master, year_gz, relations, luck)
    return {
        "target_year": target_year,
        "year_ganzhi": year_gz,
        "current_luck": luck,
        "flow_year": {
            "ganzhi": year_gz,
            "stem_ten_god": ten_god(day_master, year_gz[0]),
            "hidden_stems": [
                {"stem": stem, "ten_god": ten_god(day_master, stem)}
                for stem in HIDDEN_STEMS[flow_branch]
            ],
        },
        "activated_relations": relations,
        "activated_palaces": _activated_palaces(payload["pillars"], flow_branch),
        "event_candidates": candidates,
        "conflicts": _conflicts(candidates, relations),
    }


def _current_luck(luck: dict | None, target_year: int, birth_year_text: str) -> dict | None:
    if not luck:
        return None
    age = target_year - int(birth_year_text) + 1
    for cycle in luck["cycles"]:
        if cycle["start_age_years"] <= age < cycle["end_age_years"]:
            return {**cycle, "virtual_age": age}
    return None


def _relations_with_chart(pillars: list[dict], flow_branch: str) -> list[dict]:
    result = []
    for pillar in pillars:
        branch = pillar["branch"]
        field = f"流年支与{pillar['name']}"
        if branch == flow_branch:
            result.append({"type": "并临", "field": field, "branches": branch + flow_branch, "meaning": f"引动{pillar['name']}宫位"})
        if BRANCH_OPPOSITE[branch] == flow_branch:
            result.append({"type": "冲", "field": field, "branches": _pair(branch, flow_branch), "meaning": f"冲动{pillar['name']}宫位"})
        if BRANCH_PUNISH.get(branch) == flow_branch:
            result.append({"type": "刑", "field": field, "branches": _pair(branch, flow_branch), "meaning": f"{pillar['name']}有刑动、压力、反复"})
    return result


def _relations_with_luck(luck_branch: str, flow_branch: str) -> list[dict]:
    result = []
    if luck_branch == flow_branch:
        result.append({"type": "并临", "field": "流年支与大运支", "branches": luck_branch + flow_branch, "meaning": "流年与大运主题同位"})
    if BRANCH_OPPOSITE[luck_branch] == flow_branch:
        result.append({"type": "冲", "field": "流年支与大运支", "branches": _pair(luck_branch, flow_branch), "meaning": "流年冲动大运背景"})
    if BRANCH_PUNISH.get(luck_branch) == flow_branch:
        result.append({"type": "刑", "field": "流年支与大运支", "branches": _pair(luck_branch, flow_branch), "meaning": "大运流年刑动，压力和反复增强"})
    return result


def _activated_palaces(pillars: list[dict], flow_branch: str) -> list[dict]:
    return [
        {"pillar": pillar["name"], "branch": pillar["branch"], "reason": "流年支同位"}
        for pillar in pillars
        if pillar["branch"] == flow_branch
    ]


def _event_candidates(day_master: str, year_gz: str, relations: list[dict], luck: dict | None) -> list[dict]:
    flow_stem_god = ten_god(day_master, year_gz[0])
    hidden_gods = [ten_god(day_master, stem) for stem in HIDDEN_STEMS[year_gz[1]]]
    candidates = []
    if any(god in {"正官", "七杀", "正印", "偏印", "食神", "伤官"} for god in [flow_stem_god, *hidden_gods]):
        candidates.append({
            "domain": "学业/考试/规则压力",
            "strength": "中象",
            "evidence": [f"流年{year_gz}含{flow_stem_god}与{','.join(hidden_gods)}", "官印食伤为学习、考试、规则、训练的重要取象"],
        })
    if flow_stem_god in {"正财", "偏财"}:
        candidates.append({
            "domain": "财务/资源/男命关系议题",
            "strength": "弱到中象",
            "evidence": [f"流年天干{year_gz[0]}为{flow_stem_god}", "财星可取资源、钱财、现实目标；男命也可兼看关系议题"],
        })
    if any(item["type"] in {"冲", "刑", "并临"} for item in relations):
        candidates.append({
            "domain": "状态变化/环境触发",
            "strength": "中象",
            "evidence": [f"{item['field']}见{item['type']}" for item in relations[:3]],
        })
    return candidates


def _conflicts(candidates: list[dict], relations: list[dict]) -> list[str]:
    conflicts = []
    if len(candidates) > 2:
        conflicts.append("事件候选超过两个，最终输出需按证据收敛为主象和最多一个次象。")
    if any(item["type"] == "刑" for item in relations):
        conflicts.append("刑动可表示压力、反复或训练，不可单独定凶事。")
    return conflicts


def _pair(left: str, right: str) -> str:
    return "".join(sorted((left, right), key=BRANCHES.index))
```

- [ ] **Step 4: Run tests and fix exact expectations**

Run:

```bash
uv run python -m pytest tests/test_bazi_analysis.py -q
```

Expected: PASS after adjusting only genuinely incorrect expected values, not weakening assertions.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/bazi_analysis.py tests/test_bazi_analysis.py
git commit -m "Add bazi year analysis hints"
```

---

### Task 3: Add 八字 Session Script

**Files:**
- Create: `bazi_session.py`
- Create: `tools_bazi_session_wrapper.py`
- Test: `tests/test_bazi_session.py`

- [ ] **Step 1: Write failing session tests**

Create `tests/test_bazi_session.py`:

```python
import json

from bazi_session import main


def _extract_json(output: str) -> dict:
    start = output.index("```json") + len("```json")
    end = output.index("```", start)
    return json.loads(output[start:end].strip())


def test_bazi_session_outputs_chart_hints_and_rule_cards(capsys):
    assert main([
        "2006-12-18 12:30:00",
        "--gender",
        "男",
        "--target-year",
        "2025",
        "--question",
        "推断2025年发生了什么",
    ]) == 0
    payload = _extract_json(capsys.readouterr().out)

    assert payload["calendar"]["year_gz"] == "丙戌"
    assert payload["analysis_hints"]["target_year"] == 2025
    assert payload["analysis_hints"]["year_ganzhi"] == "乙巳"
    assert payload["rule_cards"]["mode"] == "year_event"


def test_bazi_session_can_include_prompt(capsys):
    assert main([
        "2006-12-18 12:30:00",
        "--gender",
        "男",
        "--target-year",
        "2025",
        "--include-prompt",
    ]) == 0
    output = capsys.readouterr().out

    assert "# 八字年份事件分析 Prompt" in output
    assert "## 八字工具上下文" in output
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run python -m pytest tests/test_bazi_session.py -q
```

Expected: FAIL with missing `bazi_session`.

- [ ] **Step 3: Implement `bazi_session.py`**

Create `bazi_session.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints
from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context


PROMPT_PATHS = (
    Path(__file__).with_name("BAZI_PROMPT.md"),
    Path(__file__).with_name("bazi_prompt.md"),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成供 Codex 分析的八字上下文。")
    parser.add_argument("datetime", nargs="?", help="出生时间，例如 '2006-12-18 12:30:00'；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--gender", choices=("男", "女"))
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--zi-hour-rule", choices=("whole", "split"), default="whole")
    parser.add_argument("--target-year", type=int)
    parser.add_argument("--question")
    parser.add_argument("--include-prompt", action="store_true")
    args = parser.parse_args(argv)

    value = args.datetime or datetime.now().isoformat(timespec="seconds")
    chart = build_bazi_chart(
        value,
        timezone=args.timezone,
        gender=args.gender,
        longitude=args.longitude,
        zi_hour_rule=args.zi_hour_rule,
    )
    payload = chart.to_dict()
    if args.target_year is not None:
        payload["analysis_hints"] = build_year_analysis_hints(chart, args.target_year)
    payload["rule_cards"] = build_bazi_rule_context(args.question, args.target_year)
    payload["question"] = args.question

    if args.include_prompt:
        print(_prompt_path().read_text(encoding="utf-8").strip())
        print("\n---\n")
    print("## 八字工具上下文\n")
    print("将下面 JSON 作为唯一八字排盘与分析提示依据；不要脱离字段自由发挥。\n")
    print("```json")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("```")
    return 0


def _prompt_path() -> Path:
    for path in PROMPT_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("未找到 BAZI_PROMPT.md 或 bazi_prompt.md")


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Create wrapper script**

Create `tools_bazi_session_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parent / "daliuren_agent"
sys.path.insert(0, str(TOOL_ROOT))

from bazi_session import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run tests**

Run:

```bash
uv run python -m pytest tests/test_bazi_session.py -q
```

Expected: Prompt test may fail until Task 4 creates `bazi_prompt.md`; keep this failure visible and proceed to Task 4.

- [ ] **Step 6: Commit after Task 4 passes**

Do not commit Task 3 alone if prompt test still fails.

---

### Task 4: Add 八字 Prompt V1

**Files:**
- Create: `bazi_prompt.md`
- Test: `tests/test_bazi_prompt_policy.py`
- Re-run: `tests/test_bazi_session.py`

- [ ] **Step 1: Write prompt policy tests**

Create `tests/test_bazi_prompt_policy.py`:

```python
from pathlib import Path


PROMPT = Path(__file__).resolve().parents[1] / "bazi_prompt.md"


def test_bazi_prompt_requires_analysis_hints_and_rule_cards():
    text = PROMPT.read_text(encoding="utf-8")

    assert "# 八字年份事件分析 Prompt" in text
    assert "没有八字盘，不做断语" in text
    assert "analysis_hints" in text
    assert "rule_cards" in text
    assert "主象" in text
    assert "次象" in text
    assert "待核验点" in text


def test_bazi_prompt_forbids_candidate_piling():
    text = PROMPT.read_text(encoding="utf-8")

    assert "禁止候选清单式断法" in text
    assert "最多一个次象" in text
    assert "必须回指" in text
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run python -m pytest tests/test_bazi_prompt_policy.py -q
```

Expected: FAIL because prompt file missing.

- [ ] **Step 3: Create `bazi_prompt.md`**

Create `bazi_prompt.md`:

```markdown
# 八字年份事件分析 Prompt

你是“东玄八字分析助手”。你的职责不是自由发挥，而是基于工具排出的八字盘、analysis_hints、rule_cards 和用户问题做结构化分析。

## 硬规则

- 没有八字盘，不做断语；先调用 `/home/source/Documents/东玄知识库/tools/bazi_session.py`。
- JSON 是唯一排盘依据；不要改写四柱、大运、流年。
- 若有 `analysis_hints`，必须优先使用其中的 `current_luck`、`flow_year`、`activated_relations`、`event_candidates`、`conflicts`。
- 若有 `rule_cards`，必须遵守每张卡的 `use_when` 与 `avoid`。
- 不做绝对化承诺。疾病、法律、投资、人身安全只给趋势和风险提示。
- 未实现的内容标注“不确定/待校验”，不要编造古籍依据。

## 分析顺序

1. 输入确认：出生时间、性别、时区、真太阳时、子时规则、目标年份、问题。
2. 命盘摘要：四柱、日主、藏干十神、地支关系、旬空、大运。
3. 运年定位：当前大运、目标流年、流年十神、流年藏干。
4. 引动结构：流年与原局、大运的冲合刑害、并临，说明引动哪个宫位。
5. 事件取象：从 `event_candidates` 中收敛为一个主象，最多一个次象。
6. 证据链：每个主象/次象必须回指具体字段，如流年干十神、流年支与日支并临、大运干支、地支刑冲。
7. 待核验点：列 1-3 个可以由用户反馈验证的具体事项。
8. 不确定项：列工具 uncertainty、analysis_hints.conflicts、规则卡 avoid 限制、未实现项。

## 收敛规则

- 禁止候选清单式断法，不得把所有十神含义逐项罗列。
- 主象必须是证据最多、与用户问题最贴近的一类事件。
- 次象只有在另一组证据稳定存在时才输出，且最多一个次象。
- 如果候选冲突，先说明冲突，再给倾向。
- 不能只凭“财星”断钱财或感情；不能只凭“官杀”断考试或灾祸；必须合大运、流年、宫位、冲合刑害。

## 输出格式

```markdown
## 输入确认

## 命盘摘要

## 运年定位

## 引动结构

## 事件取象

## 结论

## 待核验点

## 不确定项
```
```

- [ ] **Step 4: Run prompt and session tests**

Run:

```bash
uv run python -m pytest tests/test_bazi_prompt_policy.py tests/test_bazi_session.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit Tasks 3 and 4**

```bash
git add bazi_session.py bazi_prompt.md tools_bazi_session_wrapper.py tests/test_bazi_session.py tests/test_bazi_prompt_policy.py
git commit -m "Add bazi year analysis session prompt"
```

---

### Task 5: Integrate Tool Sync And Skill Notes

**Files:**
- Modify: `/home/source/.agents/skills/daliuren-divination/SKILL.md` only if reusing the same skill, or create a new skill manually later.
- Copy targets:
  - `/home/source/Documents/东玄知识库/tools/daliuren_agent/dongxuan_agent/`
  - `/home/source/Documents/东玄知识库/tools/daliuren_agent/bazi_session.py`
  - `/home/source/Documents/东玄知识库/tools/daliuren_agent/BAZI_PROMPT.md`
  - `/home/source/Documents/东玄知识库/tools/bazi_session.py`

- [ ] **Step 1: Sync package and scripts**

Run:

```bash
cp -r /home/source/My_github/dongxuan_agent/dongxuan_agent /home/source/Documents/东玄知识库/tools/daliuren_agent/
cp /home/source/My_github/dongxuan_agent/bazi_session.py /home/source/Documents/东玄知识库/tools/daliuren_agent/bazi_session.py
cp /home/source/My_github/dongxuan_agent/bazi_prompt.md /home/source/Documents/东玄知识库/tools/daliuren_agent/BAZI_PROMPT.md
cp /home/source/My_github/dongxuan_agent/tools_bazi_session_wrapper.py /home/source/Documents/东玄知识库/tools/bazi_session.py
```

- [ ] **Step 2: Verify target tool with uv**

Run:

```bash
cd /home/source/My_github/dongxuan_agent
uv run python /home/source/Documents/东玄知识库/tools/bazi_session.py "2006-12-18 12:30:00" --gender 男 --target-year 2025 --question "推断2025年发生了什么" --include-prompt
```

Expected:

- Output contains `# 八字年份事件分析 Prompt`
- Output contains `analysis_hints`
- Output contains `rule_cards`
- JSON has `analysis_hints.year_ganzhi == "乙巳"`

- [ ] **Step 3: Update skill instruction**

Append to `/home/source/.agents/skills/daliuren-divination/SKILL.md` or create a future `bazi-divination` skill:

```markdown
## 八字工具

For 八字/四柱/大运/流年 questions, use:

```bash
cd /home/source/My_github/dongxuan_agent
uv run python /home/source/Documents/东玄知识库/tools/bazi_session.py "<出生时间>" --gender 男|女 --target-year <年份> --question "<问题>" --include-prompt
```

Do not run with bare system `python3`; use `uv run python` so `sxtwl` is available.
```

- [ ] **Step 4: Commit sync-related tracked files**

Only commit repo files, not `/home/source/Documents` or skill file:

```bash
git status --short
git add .
git commit -m "Add bazi year event analysis workflow"
```

---

### Task 6: Full Verification

**Files:**
- No new files.

- [ ] **Step 1: Run full tests**

Run:

```bash
uv run python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Smoke-test chart-only still works**

Run:

```bash
uv run python /home/source/Documents/东玄知识库/tools/bazi_chart.py "2006-12-18 12:30:00" --gender 男 --format json
```

Expected: JSON has `day_master == "辛"` and `luck.direction == "顺"`.

- [ ] **Step 3: Smoke-test year-analysis session**

Run:

```bash
uv run python /home/source/Documents/东玄知识库/tools/bazi_session.py "2006-12-18 12:30:00" --gender 男 --target-year 2025 --question "推断2025年发生了什么"
```

Expected: JSON has `analysis_hints.event_candidates` and `rule_cards.cards`.

- [ ] **Step 4: Final status**

Run:

```bash
git status --short --branch
git log --oneline -5
```

Expected: clean worktree on `master`, latest commit is the 八字 analysis workflow commit.

---

## Self-Review

Spec coverage:

- 年份发生事件推断: Task 2 adds `analysis_hints` with target year, current luck, flow year, activated relations, event candidates, conflicts.
- 取象分析: Task 1 adds rule cards; Task 2 maps ten gods and branch activations to event domains.
- 联系总结与收敛: Task 4 Prompt requires 主象/次象 and forbids candidate piling.
- Tool workflow: Task 3 adds session; Task 5 syncs target tools and skill instruction.
- Testing: Every task has failing tests first and exact verification commands.

Placeholder scan:

- No `TBD`, `TODO`, or unspecified “write tests” steps remain.
- Code snippets define all referenced functions.

Type consistency:

- `analysis_hints`, `rule_cards`, `event_candidates`, `current_luck`, and `target_year` names are consistent across tests, implementation, and prompt.

