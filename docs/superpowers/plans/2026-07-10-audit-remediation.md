# Audit Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the unused Web stack, correct Bazi boundary behavior, make local knowledge and prompts portable, and establish a verified `master` baseline.

**Architecture:** Keep the three divination domains as a CLI-first Python package. Centralize local knowledge discovery in `dongxuan_agent.core`, package prompts with `importlib.resources`, and express Bazi luck matching as explicit status instead of fabricated fallback data.

**Tech Stack:** Python 3.11+, sxtwl, pytest, mypy, Ruff, setuptools, uv, GitHub Actions.

---

### Task 1: Remove the Web and Docker feature set

**Files:**
- Create: `tests/test_project_boundaries.py`
- Modify: `pyproject.toml`
- Delete: `dongxuan_agent/web/`
- Delete: `tests/test_web_app.py`
- Delete: `tests/test_web_auth_audit.py`
- Delete: `tests/test_web_memory.py`
- Delete: `tests/test_docker_config.py`
- Delete: `Dockerfile`
- Delete: `docker-compose.yml`
- Delete: `.dockerignore`
- Delete: `.env.example`
- Delete: `scripts/start-readonly-web.sh`
- Delete: `docs/docker-web.md`

- [ ] **Step 1: Write the failing project-boundary test**

```python
from pathlib import Path
import tomllib


def test_web_and_docker_features_are_removed():
    assert not Path("dongxuan_agent/web").exists()
    assert not Path("Dockerfile").exists()
    assert not Path("docker-compose.yml").exists()
    assert not Path("scripts/start-readonly-web.sh").exists()


def test_runtime_dependencies_only_contain_domain_engine():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["dependencies"] == ["sxtwl"]
```

- [ ] **Step 2: Run the boundary test and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_project_boundaries.py -v`

Expected: FAIL because Web/Docker files exist and runtime dependencies contain FastAPI, HTTPX, and Uvicorn.

- [ ] **Step 3: Delete the feature and trim dependencies**

Set the runtime dependency block to:

```toml
dependencies = ["sxtwl"]
```

Use `git rm` for every listed tracked Web, Docker, deployment, and test file.

- [ ] **Step 4: Run focused and full tests**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_project_boundaries.py -v`

Expected: PASS.

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest -q`

Expected: all remaining tests pass with no FastAPI warning.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/test_project_boundaries.py
git commit -m "refactor: remove web runtime"
```

### Task 2: Standardize the early/late Zi-hour boundary and validate longitude

**Files:**
- Modify: `dongxuan_agent/bazi/chart.py`
- Modify: `dongxuan_agent/bazi/context.py`
- Modify: `dongxuan_agent/bazi/cli.py`
- Modify: `dongxuan_agent/apps/sessions/bazi.py`
- Modify: `tests/test_bazi.py`
- Modify: `tests/test_bazi_cli.py`
- Modify: `tests/test_bazi_context.py`
- Modify: `tests/test_bazi_session.py`

- [ ] **Step 1: Replace legacy rule tests with the approved behavior**

```python
def test_bazi_chart_uses_midnight_as_day_boundary_for_zi_hour():
    late = build_bazi_chart("2026-05-25 23:30:00", timezone="Asia/Shanghai")
    early = build_bazi_chart("2026-05-26 00:30:00", timezone="Asia/Shanghai")

    assert late.calendar.day_gz == "己亥"
    assert late.calendar.hour_gz == "甲子"
    assert early.calendar.day_gz == "庚子"
    assert early.calendar.hour_gz == "丙子"
    assert late.time_rules == {
        "day_boundary": "24:00",
        "zi_hour_rule": "early_late_split",
        "note": "早晚子时，以 24:00 为日界；23:00-23:59 属当天晚子时，00:00-00:59 属当日早子时。",
    }


@pytest.mark.parametrize("longitude", [-180.0, 180.0])
def test_bazi_chart_accepts_longitude_boundaries(longitude):
    assert build_bazi_chart("2026-05-26 10:14:15", longitude=longitude)


@pytest.mark.parametrize("longitude", [-180.01, 180.01, float("nan"), float("inf"), float("-inf")])
def test_bazi_chart_rejects_invalid_longitude(longitude):
    with pytest.raises(ValueError, match="经度必须是 -180 到 180 之间的有限数"):
        build_bazi_chart("2026-05-26 10:14:15", longitude=longitude)
```

Remove all test calls that pass `zi_hour_rule` and assert that CLI help no longer exposes `--zi-hour-rule`.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi.py tests/test_bazi_cli.py tests/test_bazi_context.py tests/test_bazi_session.py -v`

Expected: FAIL because the old selector still exists, metadata differs, and invalid longitude is accepted.

- [ ] **Step 3: Implement the single approved rule**

Use the normal calendar day directly and remove `_bazi_calendar` plus the `zi_hour_rule` parameter:

```python
def build_bazi_chart(
    value,
    *,
    timezone: str = "Asia/Shanghai",
    gender: str | None = None,
    longitude: float | None = None,
) -> BaziChart:
    adjusted_value, time_adjustment = _adjust_time(value, timezone, longitude)
    calendar = get_calendar_info(adjusted_value, timezone)
    # existing pillar construction remains unchanged
```

Validate longitude before calculating an offset:

```python
if longitude is not None and (not math.isfinite(longitude) or not -180 <= longitude <= 180):
    raise ValueError("经度必须是 -180 到 180 之间的有限数")
```

Return `mode: longitude_approximation` and the rule text `经度每差 1 度折 4 分钟；仅为经度近似校正，未加入均时差。` when longitude is supplied. Remove the selector from context, CLI, and session signatures.

- [ ] **Step 4: Verify GREEN and regression safety**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi.py tests/test_bazi_cli.py tests/test_bazi_context.py tests/test_bazi_session.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/bazi tests/test_bazi.py tests/test_bazi_cli.py tests/test_bazi_context.py tests/test_bazi_session.py
git commit -m "fix: standardize bazi zi-hour boundary"
```

### Task 3: Represent Bazi luck matching without fabricated fallbacks

**Files:**
- Modify: `dongxuan_agent/bazi/year.py`
- Modify: `dongxuan_agent/bazi/integration.py`
- Modify: `dongxuan_agent/bazi/luck_remedy.py`
- Modify: `tests/test_bazi_analysis.py`
- Modify: `tests/test_bazi_integration.py`
- Modify: `tests/test_bazi_remedy_god_luck.py`

- [ ] **Step 1: Add failing status and downstream tests**

```python
def test_year_before_birth_is_rejected():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")
    with pytest.raises(ValueError, match="目标年份不能早于出生年份"):
        build_year_analysis_hints(chart, 2005)


def test_year_before_luck_start_has_no_current_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")
    hints = build_year_analysis_hints(chart, 2006)
    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "not_started"


def test_year_beyond_generated_cycles_has_no_fallback_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00", gender="男")
    hints = build_year_analysis_hints(chart, 2200)
    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "out_of_range"


def test_year_without_gender_reports_unavailable_luck():
    chart = build_bazi_chart("2006-12-18 12:30:00")
    hints = build_year_analysis_hints(chart, 2025)
    assert hints["current_luck"] is None
    assert hints["luck_status"]["status"] == "unavailable"
```

Add integration assertions that an absent luck returns `ganzhi: None`, retains flow-year analysis, and includes the status message in `uncertainty`.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi_analysis.py tests/test_bazi_integration.py tests/test_bazi_remedy_god_luck.py -v`

Expected: FAIL because pre-start and out-of-range years return cycle 8 and `luck_status` does not exist.

- [ ] **Step 3: Implement explicit matching status**

```python
def _match_current_luck(payload: dict, target_year: int) -> tuple[dict | None, dict]:
    birth_year = datetime.fromisoformat(payload["calendar"]["datetime"]).year
    if target_year < birth_year:
        raise ValueError("目标年份不能早于出生年份")
    virtual_age = target_year - birth_year + 1
    cycles = (payload.get("luck") or {}).get("cycles") or []
    if not cycles:
        return None, {"status": "unavailable", "virtual_age": virtual_age, "message": "未提供有效性别，无法生成大运。"}
    if virtual_age < cycles[0]["start_age_years"]:
        return None, {"status": "not_started", "virtual_age": virtual_age, "message": "目标年份尚未起运。"}
    for cycle in cycles:
        if cycle["start_age_years"] <= virtual_age < cycle["end_age_years"]:
            current = {**cycle, "virtual_age": virtual_age, "match_rule": "按目标年虚岁落入大运区间匹配。"}
            return current, {"status": "matched", "virtual_age": virtual_age, "message": "已匹配当前大运。"}
    return None, {"status": "out_of_range", "virtual_age": virtual_age, "message": "目标年份超出已生成大运范围。"}
```

Store both values in `build_year_analysis_hints`. Pass `luck_status` to integration and remedy output so absent luck is described by its actual reason rather than “未提供性别”.

- [ ] **Step 4: Verify GREEN and run all Bazi tests**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi_analysis.py tests/test_bazi_integration.py tests/test_bazi_remedy_god_luck.py -v`

Expected: PASS.

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi*.py -q`

Expected: all Bazi tests pass.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/bazi/year.py dongxuan_agent/bazi/integration.py dongxuan_agent/bazi/luck_remedy.py tests/test_bazi_analysis.py tests/test_bazi_integration.py tests/test_bazi_remedy_god_luck.py
git commit -m "fix: model bazi luck boundaries explicitly"
```

### Task 4: Stop target years from injecting unrelated rule cards

**Files:**
- Modify: `dongxuan_agent/bazi/rule_cards.py`
- Modify: `tests/test_bazi_rule_cards.py`

- [ ] **Step 1: Add a failing generic-year test and correct domain expectations**

```python
def test_target_year_does_not_add_unasked_domain_cards():
    context = build_bazi_rule_context(question="推断2025年发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}
    assert "学业/考试取象" not in names
    assert "财务/资源取象" not in names


def test_target_year_only_adds_domains_named_in_question():
    context = build_bazi_rule_context(question="2025年学业和感情发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}
    assert "学业/考试取象" in names
    assert "感情/关系取象" in names
    assert "财务/资源取象" not in names
```

- [ ] **Step 2: Run and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi_rule_cards.py -v`

Expected: FAIL because target years append both study and finance cards.

- [ ] **Step 3: Remove unconditional domain injection**

Keep domain selection exclusively as:

```python
selected_domains = [
    domain
    for domain, keywords in QUESTION_KEYWORDS.items()
    if any(keyword in question for keyword in keywords)
]
cards.extend(DOMAIN_CARDS[domain] for domain in selected_domains)
```

- [ ] **Step 4: Verify GREEN and commit**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_bazi_rule_cards.py -v`

Expected: PASS.

```bash
git add dongxuan_agent/bazi/rule_cards.py tests/test_bazi_rule_cards.py
git commit -m "fix: select bazi rule cards from question"
```

### Task 5: Centralize and sanitize local knowledge access

**Files:**
- Create: `dongxuan_agent/core/knowledge.py`
- Create: `tests/test_knowledge_config.py`
- Modify: `dongxuan_agent/bazi/knowledge.py`
- Modify: `dongxuan_agent/bazi/imagery.py`
- Modify: `dongxuan_agent/daliuren/knowledge.py`
- Modify: `tests/test_bazi_imagery.py`
- Modify: `tests/test_bazi_context.py`
- Modify: `tests/test_session.py`

- [ ] **Step 1: Add failing resolver, degradation, and redaction tests**

```python
def test_knowledge_root_prefers_environment(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    root.mkdir()
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    location = resolve_knowledge_location()
    assert location.root == root
    assert location.status == "available"


def test_missing_knowledge_root_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(tmp_path / "missing"))
    location = resolve_knowledge_location()
    assert location.status == "missing"


def test_malformed_symbolic_layers_degrades_without_absolute_path(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    (root / "structured").mkdir(parents=True)
    (root / "structured" / "bazi_symbolic_layers.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))
    context = build_bazi_context("2006-12-18 12:30:00")
    serialized = json.dumps(context, ensure_ascii=False)
    assert context["knowledge_layers"]["availability"]["status"] == "invalid"
    assert str(tmp_path) not in serialized
```

Add assertions that source paths are relative, such as `topics/八字.md`, never `/home/source/...`.

- [ ] **Step 2: Run and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_knowledge_config.py tests/test_bazi_imagery.py tests/test_bazi_context.py tests/test_session.py -v`

Expected: FAIL because the resolver does not exist, roots are module-level absolutes, and malformed JSON raises.

- [ ] **Step 3: Implement the shared resolver and safe JSON reader**

```python
@dataclass(frozen=True)
class KnowledgeLocation:
    root: Path
    status: Literal["available", "missing", "unreadable"]
    source: Literal["environment", "default"]


def resolve_knowledge_location() -> KnowledgeLocation:
    configured = os.getenv("DONGXUAN_KNOWLEDGE_ROOT")
    root = Path(configured).expanduser() if configured else Path("/home/source/Documents/东玄知识库/wiki")
    source = "environment" if configured else "default"
    if not root.exists():
        return KnowledgeLocation(root, "missing", source)
    if not root.is_dir() or not os.access(root, os.R_OK):
        return KnowledgeLocation(root, "unreadable", source)
    return KnowledgeLocation(root, "available", source)


def relative_source(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_knowledge_json(path: Path) -> tuple[dict, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, "missing"
    except (OSError, json.JSONDecodeError):
        return {}, "invalid"
    return (payload, "available") if isinstance(payload, dict) else ({}, "invalid")
```

Resolve paths at call time so tests and CLI environment overrides work. Replace absolute `path` output with relative `source` fields and add a shared `availability` object to Bazi and Daliuren knowledge contexts.

- [ ] **Step 4: Verify GREEN and scan for leaked absolute paths**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_knowledge_config.py tests/test_bazi_imagery.py tests/test_bazi_context.py tests/test_session.py -v`

Expected: PASS.

Run: `rg -n '/home/source' dongxuan_agent prompts tests -g '*.py' -g '*.md'`

Expected: only the approved default path in `dongxuan_agent/core/knowledge.py` and test fixtures; no path in prompts or serialized expected payloads.

- [ ] **Step 5: Commit**

```bash
git add dongxuan_agent/core/knowledge.py dongxuan_agent/bazi/knowledge.py dongxuan_agent/bazi/imagery.py dongxuan_agent/daliuren/knowledge.py tests/test_knowledge_config.py tests/test_bazi_imagery.py tests/test_bazi_context.py tests/test_session.py
git commit -m "refactor: centralize local knowledge access"
```

### Task 6: Package prompts as Python resources

**Files:**
- Create: `dongxuan_agent/resources/__init__.py`
- Create: `dongxuan_agent/resources/prompts/__init__.py`
- Move: `prompts/bazi.md` to `dongxuan_agent/resources/prompts/bazi.md`
- Move: `prompts/daliuren.md` to `dongxuan_agent/resources/prompts/daliuren.md`
- Move: `prompts/liuyao.md` to `dongxuan_agent/resources/prompts/liuyao.md`
- Modify: `dongxuan_agent/apps/prompts.py`
- Modify: `pyproject.toml`
- Modify: `tests/test_prompt_resolver.py`
- Modify: `tests/test_bazi_prompt_policy.py`
- Modify: `tests/test_liuyao_prompt_policy.py`
- Modify: `tests/test_prompt_policy.py`
- Create: `tests/test_package_resources.py`

- [ ] **Step 1: Write failing resource-location tests**

```python
def test_prompt_labels_are_package_relative():
    assert prompt_label("bazi") == "dongxuan_agent/resources/prompts/bazi.md"
    assert prompt_label("daliuren") == "dongxuan_agent/resources/prompts/daliuren.md"
    assert prompt_label("liuyao") == "dongxuan_agent/resources/prompts/liuyao.md"


def test_all_packaged_prompts_are_readable():
    assert "# 八字年份事件分析 Prompt" in read_prompt("bazi")
    assert "# 大六壬测算 Prompt" in read_prompt("daliuren")
    assert "# 六爻分析 Prompt" in read_prompt("liuyao")


def test_prompt_text_has_no_machine_specific_tool_path():
    for name in ("bazi", "daliuren", "liuyao"):
        assert "/home/source" not in read_prompt(name)
```

- [ ] **Step 2: Run and verify RED**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_prompt_resolver.py tests/test_package_resources.py -v`

Expected: FAIL because prompts are repository-root files and contain absolute tool paths.

- [ ] **Step 3: Move resources and implement `importlib.resources` loading**

```python
from importlib.resources import files

PROMPT_PACKAGE = "dongxuan_agent.resources.prompts"


def prompt_label(name: PromptName) -> str:
    return f"dongxuan_agent/resources/prompts/{PROMPT_FILES[name]}"


def read_prompt(name: PromptName) -> str:
    return files(PROMPT_PACKAGE).joinpath(PROMPT_FILES[name]).read_text(encoding="utf-8")
```

Remove the filesystem-only `prompt_path` API. Update prompt policy tests to use `read_prompt`. Replace absolute command examples in the Markdown with installed commands such as `bazi-chart`, `daliuren-chart`, and the JSON context contract.

Add build metadata:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[tool.setuptools.package-data]
"dongxuan_agent.resources.prompts" = ["*.md"]
```

- [ ] **Step 4: Verify tests and wheel contents**

Run: `/home/source/My_github/dongxuan_agent/.venv/bin/python -m pytest tests/test_prompt_resolver.py tests/test_package_resources.py tests/test_bazi_prompt_policy.py tests/test_liuyao_prompt_policy.py tests/test_prompt_policy.py -v`

Expected: PASS.

Run: `UV_CACHE_DIR=/tmp/dongxuan-uv-cache uv build`

Expected: source distribution and wheel build successfully; wheel contains all three Markdown prompt files.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml dongxuan_agent/resources dongxuan_agent/apps/prompts.py tests
git commit -m "build: package prompt resources"
```

### Task 7: Add documentation, typing, lint, and CI gates

**Files:**
- Create: `README.md`
- Create: `.github/workflows/ci.yml`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `dongxuan_agent/bazi/remedy.py`
- Modify: `dongxuan_agent/bazi/discipline.py`
- Modify: `dongxuan_agent/bazi/imagery.py`
- Modify: `dongxuan_agent/bazi/strength.py`
- Modify: `dongxuan_agent/bazi/climate.py`
- Modify: `dongxuan_agent/daliuren/chart.py`
- Modify: `dongxuan_agent/daliuren/spirits.py`
- Modify: `dongxuan_agent/daliuren/transmissions.py`

- [ ] **Step 1: Record the current failing quality baseline**

Run: `mypy --ignore-missing-imports dongxuan_agent`

Expected: FAIL with the existing typed-container, protocol, and dictionary inference errors.

Run: `ruff check dongxuan_agent tests`

Expected: FAIL before Ruff fixes are applied, or command unavailable until the dev dependency is synced.

- [ ] **Step 2: Add explicit quality configuration and dependencies**

```toml
[dependency-groups]
dev = [
    "mypy>=1.18",
    "pytest>=9.0.3",
    "ruff>=0.12",
]

[tool.mypy]
python_version = "3.11"
files = ["dongxuan_agent"]
ignore_missing_imports = true

[tool.ruff]
target-version = "py311"
line-length = 120

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I"]
```

Run `uv lock` to remove Web packages and lock the quality tools.

- [ ] **Step 3: Fix the reported types without global ignores**

Use explicit local container types where heterogeneous dictionaries are built:

```python
problems: list[dict[str, object]] = []
candidates: list[dict[str, object]] = []
conflicts: list[str] = []
scores: dict[str, dict[str, Any]] = {...}
result: dict[str, list[dict[str, object]]] = {"supported": [], "weakened": [], "excluded": []}
strengths: dict[str, dict[str, Any]] = {}
forces: dict[str, dict[str, Any]] = {...}
preferred_elements: list[str] = []
```

Make `LessonLike` attributes read-only protocol properties so frozen `Lesson` structurally conforms:

```python
class LessonLike(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def lower(self) -> str: ...
    @property
    def upper(self) -> str: ...
    @property
    def relation(self) -> str: ...
    @property
    def lower_branch(self) -> str: ...
```

Annotate Daliuren transmission detail dictionaries as `dict[str, str | None]` and keep spirit rule collections in separately typed variables instead of assigning a list over a dictionary-inferred name.

- [ ] **Step 4: Add README and CI**

README must document installation with `uv sync`, the three chart commands, session entrypoints, `DONGXUAN_KNOWLEDGE_ROOT`, the 24:00 early/late Zi-hour boundary, longitude approximation, tests, and the fact that no Web server is included.

Use this CI job shape:

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.11", "3.13"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --frozen --all-groups
      - run: uv run ruff check dongxuan_agent tests
      - run: uv run mypy dongxuan_agent
      - run: uv run pytest -q
      - run: uv run python -m compileall -q dongxuan_agent
      - run: uv build
```

- [ ] **Step 5: Run format-safe fixes and verify the gates**

Run: `uv run ruff check --fix dongxuan_agent tests`

Run: `uv run ruff check dongxuan_agent tests`

Expected: PASS.

Run: `uv run mypy dongxuan_agent`

Expected: `Success: no issues found`.

Run: `uv run pytest -q`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add README.md .github/workflows/ci.yml pyproject.toml uv.lock dongxuan_agent tests
git commit -m "ci: enforce project quality gates"
```

### Task 8: Final verification, authorized data deletion, and master integration

**Files:**
- Delete from primary workspace: `.env`
- Delete from primary workspace: `.dongxuan/`
- Delete from primary workspace: `data/runtime/`
- Delete from primary workspace: `dongxuan-data/`
- Preserve in primary workspace: `.superpowers/`

- [ ] **Step 1: Run the complete verification suite on the fix branch**

```bash
uv run ruff check dongxuan_agent tests
uv run mypy dongxuan_agent
uv run pytest -q
uv run python -m compileall -q dongxuan_agent
UV_CACHE_DIR=/tmp/dongxuan-uv-cache uv build
git diff --check
git status --short --branch
```

Expected: every command exits 0 and the fix branch is clean.

- [ ] **Step 2: Delete only the explicitly authorized local data**

First verify the exact paths with `ls -ld` without reading contents, then permanently delete:

```bash
rm -rf /home/source/My_github/dongxuan_agent/.env \
       /home/source/My_github/dongxuan_agent/.dongxuan \
       /home/source/My_github/dongxuan_agent/data/runtime \
       /home/source/My_github/dongxuan_agent/dongxuan-data
```

Confirm `.superpowers/` still exists and remains untracked.

- [ ] **Step 3: Fast-forward `master` to the verified fix branch**

```bash
git -C /home/source/My_github/dongxuan_agent merge --ff-only fix/audit-remediation
```

Expected: `master` fast-forwards from `0bbc4d5` through the feature history and remediation commits.

- [ ] **Step 4: Re-run verification from the primary workspace**

```bash
uv run ruff check dongxuan_agent tests
uv run mypy dongxuan_agent
uv run pytest -q
uv run python -m compileall -q dongxuan_agent
UV_CACHE_DIR=/tmp/dongxuan-uv-cache uv build
git status --short --branch
```

Expected: all checks pass; only `.superpowers/` may remain untracked.

- [ ] **Step 5: Remove temporary branch/worktree metadata after verification**

From the primary workspace, remove the linked worktree, then delete fully merged local branches `fix/audit-remediation` and `feature/liuyao-tool-mvp`. Do not delete or push remote branches.
