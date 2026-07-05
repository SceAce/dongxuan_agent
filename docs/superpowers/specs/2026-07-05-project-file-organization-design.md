# Dongxuan Project File Organization Design

## Goal

Reorganize the repository so files are grouped by responsibility instead of by creation order. The final layout should make these boundaries obvious:

- domain code: 大六壬、八字、六爻
- shared foundations: calendar, constants, render helpers, common metaphysics utilities
- application entry points: chart CLIs, session/context generators, web runtime
- external tool wrappers under `tools/`
- prompt assets under `prompts/`
- runtime data under `data/runtime/`, excluded from git

The cleanup should be structural and behavior-preserving. Existing external calls should continue to work through compatibility wrappers while internal code moves to the new layout.

## Current Problems

The current project root mixes configuration, prompts, session generators, tool wrappers, runtime data, and Python package code. The largest issues are:

- `bazi_session.py`, `daliuren_session.py`, and `liuyao_session.py` are root-level application code.
- `bazi_prompt.md`, `daliuren_prompt.md`, and `liuyao_prompt.md` are root-level assets.
- `tools_*_wrapper.py` files live in the root while the new `tools/` directory is empty.
- `dongxuan_agent/` contains both domain modules and shared infrastructure in the same package level.
- 八字 has already moved most implementation to `dongxuan_agent/bazi/`, but old `dongxuan_agent/bazi_*.py` modules remain as compatibility shims.
- Runtime data is split between `.dongxuan/` and `dongxuan-data/`; `dongxuan-data/` is currently root-owned and should not be modified directly during cleanup.

## Target Layout

```text
.
├── dongxuan_agent/
│   ├── core/
│   │   ├── calendar_engine.py
│   │   ├── constants.py
│   │   ├── render.py
│   │   ├── season.py
│   │   └── xun.py
│   ├── daliuren/
│   │   ├── chart.py
│   │   ├── cli.py
│   │   ├── divination.py
│   │   ├── knowledge.py
│   │   ├── render.py
│   │   ├── rule_cards.py
│   │   ├── spirits.py
│   │   └── transmissions.py
│   ├── bazi/
│   │   ├── __init__.py
│   │   ├── chart.py
│   │   ├── cli.py
│   │   ├── climate.py
│   │   ├── context.py
│   │   ├── discipline.py
│   │   ├── gods.py
│   │   ├── imagery.py
│   │   ├── integration.py
│   │   ├── knowledge.py
│   │   ├── luck_remedy.py
│   │   ├── pattern.py
│   │   ├── remedy.py
│   │   ├── rule_cards.py
│   │   ├── spirits.py
│   │   ├── strength.py
│   │   └── year.py
│   ├── liuyao/
│   │   ├── __init__.py
│   │   ├── advance_retreat.py
│   │   ├── chart.py
│   │   ├── cli.py
│   │   ├── combinations.py
│   │   ├── context.py
│   │   ├── flying_hidden.py
│   │   ├── hexagrams.py
│   │   ├── imagery.py
│   │   ├── judgment.py
│   │   ├── najia.py
│   │   ├── question.py
│   │   ├── relations.py
│   │   ├── six_spirits.py
│   │   ├── spirit_roles.py
│   │   ├── spirit_sha.py
│   │   ├── strength.py
│   │   ├── templates.py
│   │   ├── timing.py
│   │   └── twelve_stages.py
│   ├── apps/
│   │   └── sessions/
│   │       ├── bazi.py
│   │       ├── daliuren.py
│   │       └── liuyao.py
│   ├── compat/
│   │   ├── bazi.py
│   │   ├── daliuren.py
│   │   └── liuyao.py
│   └── web/
├── tools/
│   ├── bazi/
│   │   ├── chart_wrapper.py
│   │   └── session_wrapper.py
│   ├── daliuren/
│   │   ├── chart_wrapper.py
│   │   └── session_wrapper.py
│   └── liuyao/
│       ├── chart_wrapper.py
│       └── session_wrapper.py
├── prompts/
│   ├── bazi.md
│   ├── daliuren.md
│   └── liuyao.md
├── data/
│   ├── runtime/
│   └── samples/
├── docs/
├── scripts/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

Root-level compatibility files will remain during this cleanup:

- `bazi_session.py`
- `daliuren_session.py`
- `liuyao_session.py`
- `tools_bazi_chart_wrapper.py`
- `tools_bazi_session_wrapper.py`
- `tools_daliuren_chart_wrapper.py`
- `tools_daliuren_session_wrapper.py`
- `tools_liuyao_chart_wrapper.py`
- `tools_liuyao_session_wrapper.py`

Each root compatibility file should only import and call the relocated implementation.

## Module Migration

### Shared Core

Move shared foundations to `dongxuan_agent/core/`:

- `calendar_engine.py`
- `constants.py`
- `season.py`
- `xun.py`

`render.py` should be split carefully. 大六壬-specific render functions should move to `dongxuan_agent/daliuren/render.py`; only genuinely shared rendering helpers should remain in `core`.

### 大六壬

Move 大六壬 domain modules from package root to `dongxuan_agent/daliuren/`:

- `chart.py`
- `cli.py`
- `divination.py`
- `daliuren_knowledge.py` to `knowledge.py`
- `rule_cards.py`
- `spirits.py`
- `transmissions.py`

The existing public script `daliuren-chart = "dongxuan_agent.cli:main"` should be updated to `dongxuan_agent.daliuren.cli:main`. The old `dongxuan_agent/cli.py` should remain as a compatibility wrapper during this cleanup.

### 八字

Keep the existing `dongxuan_agent/bazi/` package as the canonical 八字 domain. Move or rename:

- `dongxuan_agent/bazi_cli.py` to `dongxuan_agent/bazi/cli.py`
- `dongxuan_agent/bazi_knowledge.py` to `dongxuan_agent/bazi/knowledge.py`

The current `dongxuan_agent/bazi_*.py` files should stay as compatibility shims that re-export from `dongxuan_agent.bazi.*`. They are small and protect current tests and external imports.

### 六爻

Keep the existing `dongxuan_agent/liuyao/` package as the canonical 六爻 domain. Move:

- `dongxuan_agent/liuyao_cli.py` to `dongxuan_agent/liuyao/cli.py`

The old `dongxuan_agent/liuyao_cli.py` should remain as a compatibility wrapper during this cleanup.

### Sessions

Move session/context generators to `dongxuan_agent/apps/sessions/`:

- `bazi_session.py` to `dongxuan_agent/apps/sessions/bazi.py`
- `daliuren_session.py` to `dongxuan_agent/apps/sessions/daliuren.py`
- `liuyao_session.py` to `dongxuan_agent/apps/sessions/liuyao.py`

The root files should remain as wrappers that call the new modules. This preserves current tests and external usage while removing implementation logic from the root.

### Prompts

Move prompt assets to `prompts/`:

- `bazi_prompt.md` to `prompts/bazi.md`
- `daliuren_prompt.md` to `prompts/daliuren.md`
- `liuyao_prompt.md` to `prompts/liuyao.md`

Session modules and web services should resolve prompt files through `dongxuan_agent/apps/prompts.py`, so future prompt moves do not require updates in multiple places.

Root prompt files should not remain after this cleanup. Prompt policy tests and application code should read the canonical `prompts/*.md` files through the shared prompt resolver.

### Tools

Move tool wrapper implementations into `tools/<domain>/`:

- `tools_bazi_chart_wrapper.py` to `tools/bazi/chart_wrapper.py`
- `tools_bazi_session_wrapper.py` to `tools/bazi/session_wrapper.py`
- `tools_daliuren_chart_wrapper.py` to `tools/daliuren/chart_wrapper.py`
- `tools_daliuren_session_wrapper.py` to `tools/daliuren/session_wrapper.py`
- `tools_liuyao_chart_wrapper.py` to `tools/liuyao/chart_wrapper.py`
- `tools_liuyao_session_wrapper.py` to `tools/liuyao/session_wrapper.py`

Root wrapper files should remain as compatibility wrappers. The wrapper code should stop referring to a non-existent `daliuren_agent` directory and should import from this repository package directly.

### Runtime Data

Adopt `data/runtime/` as the default local runtime location:

- `data/runtime/memory.json`
- `data/runtime/audit.jsonl`
- `data/runtime/auth.json`
- `data/runtime/config.toml`

Keep Docker volume compatibility for `./dongxuan-data:/data/dongxuan` unless the user explicitly chooses to migrate Docker data. The cleanup should update documentation to explain:

- local app defaults use `data/runtime/`
- Docker defaults still mount `dongxuan-data/`
- `.dongxuan/` and `dongxuan-data/` are legacy runtime locations

Do not move or edit existing root-owned `dongxuan-data/` files during the cleanup. Treat them as existing runtime state.

## Compatibility Strategy

Compatibility wrappers should be short and explicit:

```python
from __future__ import annotations

from dongxuan_agent.apps.sessions.bazi import main

if __name__ == "__main__":
    raise SystemExit(main())
```

Old import modules should continue to work:

- `dongxuan_agent.cli`
- `dongxuan_agent.bazi_cli`
- `dongxuan_agent.liuyao_cli`
- `dongxuan_agent.bazi_analysis`
- `dongxuan_agent.bazi_climate`
- `dongxuan_agent.bazi_god`
- `dongxuan_agent.bazi_imagery`
- `dongxuan_agent.bazi_integration`
- `dongxuan_agent.bazi_luck_remedy`
- `dongxuan_agent.bazi_pattern`
- `dongxuan_agent.bazi_remedy`
- `dongxuan_agent.bazi_rule_cards`
- `dongxuan_agent.bazi_strength`

The implementation should update internal imports to canonical paths while tests keep a small set of compatibility checks.

## Web and Docker Impact

`dongxuan_agent/web/services.py` should load prompt files from the new prompt resolver. API metadata should report canonical prompt paths such as `prompts/bazi.md` and `prompts/daliuren.md`, and tests should be updated to assert those paths.

`dongxuan_agent/web/config.py` should use `data/runtime/` as the local default runtime directory. Docker environment variables already override memory and audit paths, so container behavior can remain unchanged.

`Dockerfile` and `.dockerignore` should be checked after moves. Because root compatibility files remain, the Docker build can continue copying the full project. No packaging change is required unless tests show import failures.

## Testing Strategy

The cleanup should be verified in layers:

1. Run focused tests for moved entry points:
   - `tests/test_cli.py`
   - `tests/test_bazi_cli.py`
   - `tests/test_liuyao_cli.py`
   - `tests/test_session.py`
   - `tests/test_bazi_session.py`
   - `tests/test_liuyao_session.py`
2. Run prompt policy tests after moving prompt files:
   - `tests/test_prompt_policy.py`
   - `tests/test_bazi_prompt_policy.py`
   - `tests/test_liuyao_prompt_policy.py`
3. Run web and Docker config tests:
   - `tests/test_web_app.py`
   - `tests/test_web_auth_audit.py`
   - `tests/test_web_memory.py`
   - `tests/test_docker_config.py`
4. Run the full test suite with `uv run pytest`.

If `uv run pytest` needs dependency downloads and fails due network restrictions, rerun with approved network escalation or use the available local environment if dependencies are already installed.

## Implementation Order

1. Create target package directories and shared prompt resolver.
2. Move prompt assets and update tests to canonical paths.
3. Move session implementations and replace root files with wrappers.
4. Move tool wrapper implementations under `tools/<domain>/` and replace root files with wrappers.
5. Move 八字 CLI and knowledge modules into `dongxuan_agent/bazi/`, retaining old import wrappers.
6. Move 六爻 CLI into `dongxuan_agent/liuyao/`, retaining old import wrapper.
7. Move 大六壬 domain modules into `dongxuan_agent/daliuren/`, retaining old import wrappers.
8. Move shared modules into `dongxuan_agent/core/`, updating imports and retaining compatibility wrappers only where tests or public entry points require them.
9. Update runtime data defaults and `.gitignore` for `data/runtime/`.
10. Run focused tests, then the full suite.

This order keeps each step small enough to diagnose import failures quickly.

## Out of Scope

- Rewriting domain algorithms.
- Changing CLI behavior or output format.
- Deleting compatibility wrappers in the same cleanup.
- Migrating existing root-owned Docker runtime files.
- Reformatting old design or plan documents that reference historical paths.
