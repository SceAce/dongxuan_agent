# 项目文件整理实施计划

> **面向 agent 执行者：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务执行。每个步骤使用 checkbox 语法跟踪。

**目标：** 按职责重组东玄项目文件结构，让大六壬、八字、六爻、应用入口、工具 wrapper、提示词和运行数据各归其位。

**架构：** 保留项目根目录的外部兼容入口，但把实现迁入 `dongxuan_agent/apps/`、`dongxuan_agent/<domain>/`、`tools/<domain>/`、`prompts/` 和 `data/runtime/`。`dongxuan_agent/` 包顶层不继续保留旧领域入口，内部 import 和测试统一改为 canonical 路径。

**技术栈：** Python 3.11、pytest、FastAPI、uv、Docker Compose。

---

## 文件结构总览

本计划会创建或移动这些核心文件：

- 新建: `dongxuan_agent/apps/__init__.py`
- 新建: `dongxuan_agent/apps/prompts.py`
- 新建: `dongxuan_agent/apps/sessions/__init__.py`
- 移动: `bazi_session.py` -> `dongxuan_agent/apps/sessions/bazi.py`
- 移动: `daliuren_session.py` -> `dongxuan_agent/apps/sessions/daliuren.py`
- 移动: `liuyao_session.py` -> `dongxuan_agent/apps/sessions/liuyao.py`
- 移动: `bazi_prompt.md` -> `prompts/bazi.md`
- 移动: `daliuren_prompt.md` -> `prompts/daliuren.md`
- 移动: `liuyao_prompt.md` -> `prompts/liuyao.md`
- 移动: `dongxuan_agent/bazi_cli.py` -> `dongxuan_agent/bazi/cli.py`
- 移动: `dongxuan_agent/liuyao_cli.py` -> `dongxuan_agent/liuyao/cli.py`
- 移动: `dongxuan_agent/bazi_knowledge.py` -> `dongxuan_agent/bazi/knowledge.py`
- 删除: `dongxuan_agent/bazi_analysis.py`
- 删除: `dongxuan_agent/bazi_climate.py`
- 删除: `dongxuan_agent/bazi_god.py`
- 删除: `dongxuan_agent/bazi_imagery.py`
- 删除: `dongxuan_agent/bazi_integration.py`
- 删除: `dongxuan_agent/bazi_luck_remedy.py`
- 删除: `dongxuan_agent/bazi_pattern.py`
- 删除: `dongxuan_agent/bazi_remedy.py`
- 删除: `dongxuan_agent/bazi_rule_cards.py`
- 删除: `dongxuan_agent/bazi_strength.py`
- 新建: `dongxuan_agent/daliuren/__init__.py`
- 移动: `dongxuan_agent/chart.py` -> `dongxuan_agent/daliuren/chart.py`
- 移动: `dongxuan_agent/cli.py` -> `dongxuan_agent/daliuren/cli.py`
- 移动: `dongxuan_agent/divination.py` -> `dongxuan_agent/daliuren/divination.py`
- 移动: `dongxuan_agent/daliuren_knowledge.py` -> `dongxuan_agent/daliuren/knowledge.py`
- 移动: `dongxuan_agent/render.py` -> `dongxuan_agent/daliuren/render.py`
- 移动: `dongxuan_agent/rule_cards.py` -> `dongxuan_agent/daliuren/rule_cards.py`
- 移动: `dongxuan_agent/spirits.py` -> `dongxuan_agent/daliuren/spirits.py`
- 移动: `dongxuan_agent/transmissions.py` -> `dongxuan_agent/daliuren/transmissions.py`
- 新建: `dongxuan_agent/core/__init__.py`
- 移动: `dongxuan_agent/calendar_engine.py` -> `dongxuan_agent/core/calendar_engine.py`
- 移动: `dongxuan_agent/constants.py` -> `dongxuan_agent/core/constants.py`
- 移动: `dongxuan_agent/season.py` -> `dongxuan_agent/core/season.py`
- 移动: `dongxuan_agent/xun.py` -> `dongxuan_agent/core/xun.py`
- 新建: `tools/__init__.py`
- 新建: `tools/bazi/__init__.py`
- 新建: `tools/daliuren/__init__.py`
- 新建: `tools/liuyao/__init__.py`
- 移动: `tools_bazi_chart_wrapper.py` -> `tools/bazi/chart_wrapper.py`
- 移动: `tools_bazi_session_wrapper.py` -> `tools/bazi/session_wrapper.py`
- 移动: `tools_daliuren_chart_wrapper.py` -> `tools/daliuren/chart_wrapper.py`
- 移动: `tools_daliuren_session_wrapper.py` -> `tools/daliuren/session_wrapper.py`
- 移动: `tools_liuyao_chart_wrapper.py` -> `tools/liuyao/chart_wrapper.py`
- 移动: `tools_liuyao_session_wrapper.py` -> `tools/liuyao/session_wrapper.py`

根目录最终只保留这些兼容入口：

- `bazi_session.py`
- `daliuren_session.py`
- `liuyao_session.py`
- `tools_bazi_chart_wrapper.py`
- `tools_bazi_session_wrapper.py`
- `tools_daliuren_chart_wrapper.py`
- `tools_daliuren_session_wrapper.py`
- `tools_liuyao_chart_wrapper.py`
- `tools_liuyao_session_wrapper.py`

---

### 任务 1: 建立提示词目录和 prompt resolver

**文件：**
- 新建: `dongxuan_agent/apps/__init__.py`
- 新建: `dongxuan_agent/apps/prompts.py`
- 移动: `bazi_prompt.md` -> `prompts/bazi.md`
- 移动: `daliuren_prompt.md` -> `prompts/daliuren.md`
- 移动: `liuyao_prompt.md` -> `prompts/liuyao.md`
- 修改: `bazi_session.py`
- 修改: `daliuren_session.py`
- 修改: `liuyao_session.py`
- 修改: `dongxuan_agent/web/services.py`
- 修改: `tests/test_bazi_prompt_policy.py`
- 修改: `tests/test_prompt_policy.py`
- 修改: `tests/test_liuyao_prompt_policy.py`
- 修改: `tests/test_web_app.py`
- 新建: `tests/test_prompt_resolver.py`

- [ ] **步骤 1: 写 prompt resolver 失败测试**

创建 `tests/test_prompt_resolver.py`:

```python
from pathlib import Path

from dongxuan_agent.apps.prompts import prompt_label, prompt_path, read_prompt


def test_prompt_path_points_to_canonical_prompt_dir():
    project_root = Path(__file__).resolve().parents[1]

    assert prompt_path("bazi") == project_root / "prompts" / "bazi.md"
    assert prompt_path("daliuren") == project_root / "prompts" / "daliuren.md"
    assert prompt_path("liuyao") == project_root / "prompts" / "liuyao.md"


def test_prompt_label_is_repo_relative():
    assert prompt_label("bazi") == "prompts/bazi.md"
    assert prompt_label("daliuren") == "prompts/daliuren.md"
    assert prompt_label("liuyao") == "prompts/liuyao.md"


def test_read_prompt_returns_text():
    assert "# 八字年份事件分析 Prompt" in read_prompt("bazi")
    assert "# 大六壬测算 Prompt" in read_prompt("daliuren")
    assert "# 六爻测算 Prompt" in read_prompt("liuyao")
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_prompt_resolver.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'dongxuan_agent.apps'`。

- [ ] **步骤 3: 移动提示词文件**

运行:

```bash
mkdir -p prompts
git mv bazi_prompt.md prompts/bazi.md
git mv daliuren_prompt.md prompts/daliuren.md
git mv liuyao_prompt.md prompts/liuyao.md
```

- [ ] **步骤 4: 创建 prompt resolver**

创建 `dongxuan_agent/apps/__init__.py`:

```python
"""Application entry-point helpers."""
```

创建 `dongxuan_agent/apps/prompts.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Literal


PromptName = Literal["bazi", "daliuren", "liuyao"]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = PROJECT_ROOT / "prompts"
PROMPT_FILES: dict[PromptName, str] = {
    "bazi": "bazi.md",
    "daliuren": "daliuren.md",
    "liuyao": "liuyao.md",
}


def prompt_path(name: PromptName) -> Path:
    return PROMPT_DIR / PROMPT_FILES[name]


def prompt_label(name: PromptName) -> str:
    return prompt_path(name).relative_to(PROJECT_ROOT).as_posix()


def read_prompt(name: PromptName) -> str:
    return prompt_path(name).read_text(encoding="utf-8")
```

- [ ] **步骤 5: 更新 session 文件读取提示词**

在 `bazi_session.py`, remove `Path` import and `PROMPT_PATHS` 中，新增：

```python
from dongxuan_agent.apps.prompts import read_prompt
```

替换:

```python
print(_prompt_path().read_text(encoding="utf-8").strip())
```

为:

```python
print(read_prompt("bazi").strip())
```

删除 `_prompt_path()`.

在 `daliuren_session.py`, remove `Path` import and `PROMPT_PATHS` 中，新增：

```python
from dongxuan_agent.apps.prompts import read_prompt
```

替换:

```python
print(_prompt_path().read_text(encoding="utf-8").strip())
```

为:

```python
print(read_prompt("daliuren").strip())
```

删除 `_prompt_path()`.

在 `liuyao_session.py`, remove `Path` import and `PROMPT_PATH` 中，新增：

```python
from dongxuan_agent.apps.prompts import read_prompt
```

替换:

```python
print(PROMPT_PATH.read_text(encoding="utf-8").strip())
```

为:

```python
print(read_prompt("liuyao").strip())
```

- [ ] **步骤 6: 更新 Web 服务提示词读取**

在 `dongxuan_agent/web/services.py` 中，新增：

```python
from dongxuan_agent.apps.prompts import prompt_label, read_prompt
```

删除：

```python
from pathlib import Path
```

删除：

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
```

把 `analyze_bazi()` 的提示词读取代码替换为：

```python
    prompt = read_prompt("bazi")
    analysis = adapter.analyze(system="bazi", prompt=prompt, context=context)
    return _response("bazi", context, analysis, prompt_label("bazi"))
```

把 `analyze_daliuren()` 的提示词读取代码替换为：

```python
    prompt = read_prompt("daliuren")
    analysis = adapter.analyze(system="daliuren", prompt=prompt, context=context)
    return _response("daliuren", context, analysis, prompt_label("daliuren"))
```

把 `_response()` 函数签名替换为：

```python
def _response(system: Literal["bazi", "daliuren"], context: dict, analysis: str, prompt_file: str) -> dict:
```

- [ ] **步骤 7: 更新 prompt policy 测试路径**

在 `tests/test_bazi_prompt_policy.py` 中，把 `PROMPT` 赋值替换为：

```python
from dongxuan_agent.apps.prompts import prompt_path


PROMPT = prompt_path("bazi")
```

在 `tests/test_prompt_policy.py` 中，把 `PROMPT` 赋值替换为：

```python
from dongxuan_agent.apps.prompts import prompt_path


PROMPT = prompt_path("daliuren")
```

在 `tests/test_liuyao_prompt_policy.py` 中，把 `PROMPT` 赋值替换为：

```python
from dongxuan_agent.apps.prompts import read_prompt


PROMPT = read_prompt("liuyao")
```

- [ ] **步骤 8: 更新 Web metadata 断言**

在 `tests/test_web_app.py` 中，把下面内容替换为：

```python
assert payload["meta"]["prompt_file"] == "bazi_prompt.md"
```

为:

```python
assert payload["meta"]["prompt_file"] == "prompts/bazi.md"
```

替换:

```python
assert payload["meta"]["prompt_file"] == "daliuren_prompt.md"
```

为:

```python
assert payload["meta"]["prompt_file"] == "prompts/daliuren.md"
```

- [ ] **步骤 9: 验证提示词迁移**

运行:

```bash
uv run pytest tests/test_prompt_resolver.py tests/test_bazi_prompt_policy.py tests/test_prompt_policy.py tests/test_liuyao_prompt_policy.py tests/test_bazi_session.py tests/test_session.py tests/test_liuyao_session.py tests/test_web_app.py -q
```

预期: PASS。

- [ ] **步骤 10: 提交**

运行:

```bash
git add dongxuan_agent/apps prompts bazi_session.py daliuren_session.py liuyao_session.py dongxuan_agent/web/services.py tests/test_prompt_resolver.py tests/test_bazi_prompt_policy.py tests/test_prompt_policy.py tests/test_liuyao_prompt_policy.py tests/test_web_app.py
git commit -m "refactor: move prompts to canonical directory"
```

---

### 任务 2: 移动 session 实现并保留根目录兼容入口

**文件：**
- 新建: `dongxuan_agent/apps/sessions/__init__.py`
- 移动: `bazi_session.py` -> `dongxuan_agent/apps/sessions/bazi.py`
- 移动: `daliuren_session.py` -> `dongxuan_agent/apps/sessions/daliuren.py`
- 移动: `liuyao_session.py` -> `dongxuan_agent/apps/sessions/liuyao.py`
- 新建: `bazi_session.py`
- 新建: `daliuren_session.py`
- 新建: `liuyao_session.py`
- 新建: `tests/test_session_entrypoints.py`

- [ ] **步骤 1: 写兼容入口测试**

创建 `tests/test_session_entrypoints.py`:

```python
import bazi_session
import daliuren_session
import liuyao_session
from dongxuan_agent.apps.sessions.bazi import main as bazi_main
from dongxuan_agent.apps.sessions.daliuren import main as daliuren_main
from dongxuan_agent.apps.sessions.liuyao import main as liuyao_main


def test_root_session_entrypoints_delegate_to_canonical_modules():
    assert bazi_session.main is bazi_main
    assert daliuren_session.main is daliuren_main
    assert liuyao_session.main is liuyao_main
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_session_entrypoints.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'dongxuan_agent.apps.sessions'`。

- [ ] **步骤 3: 移动 session 实现**

运行:

```bash
mkdir -p dongxuan_agent/apps/sessions
git mv bazi_session.py dongxuan_agent/apps/sessions/bazi.py
git mv daliuren_session.py dongxuan_agent/apps/sessions/daliuren.py
git mv liuyao_session.py dongxuan_agent/apps/sessions/liuyao.py
```

创建 `dongxuan_agent/apps/sessions/__init__.py`:

```python
"""Session context generators for external agent workflows."""
```

- [ ] **步骤 4: 创建根目录兼容入口**

创建 `bazi_session.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.bazi import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `daliuren_session.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.daliuren import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `liuyao_session.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.liuyao import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **步骤 5: 验证 session 行为**

运行:

```bash
uv run pytest tests/test_session_entrypoints.py tests/test_bazi_session.py tests/test_session.py tests/test_liuyao_session.py -q
```

预期: PASS。

- [ ] **步骤 6: 提交**

运行:

```bash
git add bazi_session.py daliuren_session.py liuyao_session.py dongxuan_agent/apps/sessions tests/test_session_entrypoints.py
git commit -m "refactor: move session generators into app package"
```

---

### 任务 3: 迁移八字和六爻 CLI，删除八字包顶层 shim

**文件：**
- 移动: `dongxuan_agent/bazi_cli.py` -> `dongxuan_agent/bazi/cli.py`
- 移动: `dongxuan_agent/liuyao_cli.py` -> `dongxuan_agent/liuyao/cli.py`
- 移动: `dongxuan_agent/bazi_knowledge.py` -> `dongxuan_agent/bazi/knowledge.py`
- 删除: `dongxuan_agent/bazi_analysis.py`
- 删除: `dongxuan_agent/bazi_climate.py`
- 删除: `dongxuan_agent/bazi_god.py`
- 删除: `dongxuan_agent/bazi_imagery.py`
- 删除: `dongxuan_agent/bazi_integration.py`
- 删除: `dongxuan_agent/bazi_luck_remedy.py`
- 删除: `dongxuan_agent/bazi_pattern.py`
- 删除: `dongxuan_agent/bazi_remedy.py`
- 删除: `dongxuan_agent/bazi_rule_cards.py`
- 删除: `dongxuan_agent/bazi_strength.py`
- 修改: `pyproject.toml`
- 修改: `dongxuan_agent/bazi/context.py`
- 修改: `dongxuan_agent/bazi/year.py`
- 修改: `tests/test_bazi_cli.py`
- 修改: `tests/test_liuyao_cli.py`
- 修改: `tests/test_bazi_analysis.py`
- 修改: `tests/test_bazi_pattern.py`
- 修改: `tests/test_bazi_strength_climate.py`
- 修改: `tests/test_bazi_rule_cards.py`
- 修改: `tests/test_bazi_integration.py`
- 修改: `tests/test_bazi_remedy_god_luck.py`
- 修改: `tests/test_bazi_imagery.py`
- 修改: `tests/test_bazi_spirits.py`

- [ ] **步骤 1: 写 canonical CLI/import 测试**

Modify `tests/test_bazi_cli.py` import:

```python
from dongxuan_agent.bazi.cli import main
```

Modify `tests/test_liuyao_cli.py` import:

```python
from dongxuan_agent.liuyao.cli import main as chart_main
```

In 八字 tests, apply these exact import replacements:

```text
from dongxuan_agent.bazi_analysis import build_year_analysis_hints
-> from dongxuan_agent.bazi.year import build_year_analysis_hints

from dongxuan_agent.bazi_climate import analyze_climate
-> from dongxuan_agent.bazi.climate import analyze_climate

from dongxuan_agent.bazi_god import build_god_candidates
-> from dongxuan_agent.bazi.gods import build_god_candidates

from dongxuan_agent.bazi_imagery import build_imagery_analysis
-> from dongxuan_agent.bazi.imagery import build_imagery_analysis

from dongxuan_agent.bazi_integration import build_integrated_analysis
-> from dongxuan_agent.bazi.integration import build_integrated_analysis

from dongxuan_agent.bazi_luck_remedy import analyze_luck_year_remedy
-> from dongxuan_agent.bazi.luck_remedy import analyze_luck_year_remedy

from dongxuan_agent.bazi_pattern import analyze_pattern
-> from dongxuan_agent.bazi.pattern import analyze_pattern

from dongxuan_agent.bazi_remedy import analyze_remedy
-> from dongxuan_agent.bazi.remedy import analyze_remedy

from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context
-> from dongxuan_agent.bazi.rule_cards import build_bazi_rule_context

from dongxuan_agent.bazi_strength import analyze_strength
-> from dongxuan_agent.bazi.strength import analyze_strength
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_bazi_cli.py tests/test_liuyao_cli.py tests/test_bazi_analysis.py tests/test_bazi_pattern.py tests/test_bazi_strength_climate.py tests/test_bazi_rule_cards.py tests/test_bazi_integration.py tests/test_bazi_remedy_god_luck.py tests/test_bazi_imagery.py tests/test_bazi_spirits.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'dongxuan_agent.bazi.cli'` 或 `ModuleNotFoundError: No module named 'dongxuan_agent.liuyao.cli'`。

- [ ] **步骤 3: 移动 CLI 和八字 knowledge**

运行:

```bash
git mv dongxuan_agent/bazi_cli.py dongxuan_agent/bazi/cli.py
git mv dongxuan_agent/liuyao_cli.py dongxuan_agent/liuyao/cli.py
git mv dongxuan_agent/bazi_knowledge.py dongxuan_agent/bazi/knowledge.py
```

在 `dongxuan_agent/bazi/context.py` 中，把下面内容替换为：

```python
from dongxuan_agent.bazi_knowledge import build_bazi_knowledge_context
```

为:

```python
from .knowledge import build_bazi_knowledge_context
```

- [ ] **步骤 4: 更新 console scripts**

在 `pyproject.toml` 中，把下面内容替换为：

```toml
bazi-chart = "dongxuan_agent.bazi_cli:main"
liuyao-chart = "dongxuan_agent.liuyao_cli:main"
```

为:

```toml
bazi-chart = "dongxuan_agent.bazi.cli:main"
liuyao-chart = "dongxuan_agent.liuyao.cli:main"
```

- [ ] **步骤 5: 删除八字包顶层 shim**

运行:

```bash
git rm dongxuan_agent/bazi_analysis.py
git rm dongxuan_agent/bazi_climate.py
git rm dongxuan_agent/bazi_god.py
git rm dongxuan_agent/bazi_imagery.py
git rm dongxuan_agent/bazi_integration.py
git rm dongxuan_agent/bazi_luck_remedy.py
git rm dongxuan_agent/bazi_pattern.py
git rm dongxuan_agent/bazi_remedy.py
git rm dongxuan_agent/bazi_rule_cards.py
git rm dongxuan_agent/bazi_strength.py
```

- [ ] **步骤 6: 更新八字 year 依赖**

在 `dongxuan_agent/bazi/year.py` 中，暂时保持 `year_ganzhi` import 不变，直到任务 4 迁移大六壬：

```python
from ..divination import year_ganzhi
```

任务 4 会把它替换为：

```python
from ..daliuren.divination import year_ganzhi
```

- [ ] **步骤 7: 验证八字和六爻迁移**

运行:

```bash
uv run pytest tests/test_bazi_cli.py tests/test_liuyao_cli.py tests/test_bazi_analysis.py tests/test_bazi_pattern.py tests/test_bazi_strength_climate.py tests/test_bazi_rule_cards.py tests/test_bazi_integration.py tests/test_bazi_remedy_god_luck.py tests/test_bazi_imagery.py tests/test_bazi_spirits.py tests/test_bazi_context.py tests/test_bazi_session.py tests/test_liuyao_session.py -q
```

预期: PASS。

- [ ] **步骤 8: 确认被删除的旧路径不再被测试引用**

运行:

```bash
rg -n "dongxuan_agent\\.(bazi_analysis|bazi_climate|bazi_god|bazi_imagery|bazi_integration|bazi_luck_remedy|bazi_pattern|bazi_remedy|bazi_rule_cards|bazi_strength|bazi_cli|liuyao_cli)" tests dongxuan_agent tools pyproject.toml
```

预期: 无匹配.

- [ ] **步骤 9: 提交**

运行:

```bash
git add pyproject.toml dongxuan_agent/bazi dongxuan_agent/liuyao tests
git commit -m "refactor: canonicalize bazi and liuyao package paths"
```

---

### 任务 4: 迁移大六壬领域模块到 `dongxuan_agent/daliuren/`

**文件：**
- 新建: `dongxuan_agent/daliuren/__init__.py`
- 移动: `dongxuan_agent/chart.py` -> `dongxuan_agent/daliuren/chart.py`
- 移动: `dongxuan_agent/cli.py` -> `dongxuan_agent/daliuren/cli.py`
- 移动: `dongxuan_agent/divination.py` -> `dongxuan_agent/daliuren/divination.py`
- 移动: `dongxuan_agent/daliuren_knowledge.py` -> `dongxuan_agent/daliuren/knowledge.py`
- 移动: `dongxuan_agent/render.py` -> `dongxuan_agent/daliuren/render.py`
- 移动: `dongxuan_agent/rule_cards.py` -> `dongxuan_agent/daliuren/rule_cards.py`
- 移动: `dongxuan_agent/spirits.py` -> `dongxuan_agent/daliuren/spirits.py`
- 移动: `dongxuan_agent/transmissions.py` -> `dongxuan_agent/daliuren/transmissions.py`
- 修改: `pyproject.toml`
- 修改: `dongxuan_agent/apps/sessions/daliuren.py`
- 修改: `dongxuan_agent/web/services.py`
- 修改: `dongxuan_agent/bazi/year.py`
- 修改: `tests/test_cli.py`
- 修改: `tests/test_chart.py`
- 修改: `tests/test_render.py`
- 修改: `tests/test_rule_cards.py`
- 修改: `tests/test_session.py`
- 修改: `tests/test_web_app.py`

- [ ] **步骤 1: 更新测试为 canonical 大六壬路径**

Apply these exact replacements in tests:

```text
from dongxuan_agent.cli import main
-> from dongxuan_agent.daliuren.cli import main

from dongxuan_agent.chart import build_chart
-> from dongxuan_agent.daliuren.chart import build_chart

from dongxuan_agent.divination import build_divination
-> from dongxuan_agent.daliuren.divination import build_divination

from dongxuan_agent.render import chart_to_json, divination_to_json
-> from dongxuan_agent.daliuren.render import chart_to_json, divination_to_json

from dongxuan_agent.rule_cards import build_rule_context
-> from dongxuan_agent.daliuren.rule_cards import build_rule_context
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_cli.py tests/test_chart.py tests/test_render.py tests/test_rule_cards.py tests/test_session.py tests/test_web_app.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'dongxuan_agent.daliuren'`。

- [ ] **步骤 3: 移动大六壬模块**

运行:

```bash
mkdir -p dongxuan_agent/daliuren
git mv dongxuan_agent/chart.py dongxuan_agent/daliuren/chart.py
git mv dongxuan_agent/cli.py dongxuan_agent/daliuren/cli.py
git mv dongxuan_agent/divination.py dongxuan_agent/daliuren/divination.py
git mv dongxuan_agent/daliuren_knowledge.py dongxuan_agent/daliuren/knowledge.py
git mv dongxuan_agent/render.py dongxuan_agent/daliuren/render.py
git mv dongxuan_agent/rule_cards.py dongxuan_agent/daliuren/rule_cards.py
git mv dongxuan_agent/spirits.py dongxuan_agent/daliuren/spirits.py
git mv dongxuan_agent/transmissions.py dongxuan_agent/daliuren/transmissions.py
```

创建 `dongxuan_agent/daliuren/__init__.py`:

```python
from __future__ import annotations

from .chart import DaliurenChart, build_chart
from .divination import DaliurenDivination, build_divination


__all__ = ["DaliurenChart", "DaliurenDivination", "build_chart", "build_divination"]
```

- [ ] **步骤 4: 更新大六壬内部 import**

在 `dongxuan_agent/daliuren/chart.py`, 把文件顶部 import 替换为：

```python
from dongxuan_agent.calendar_engine import CalendarInfo, get_calendar_info
from dongxuan_agent.constants import (
    BRANCH_ELEMENTS,
    BRANCHES,
    CONTROLLING,
    DAY_NOBLEMAN,
    GENERATING,
    HEAVENLY_GENERALS,
    HEAVENLY_OFFICER_NAMES,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
)
from .spirits import build_spirit_sha
from .transmissions import Transmissions, build_transmissions
from dongxuan_agent.xun import build_xun_dun
from dongxuan_agent.season import season_state
```

在 `dongxuan_agent/daliuren/divination.py`, 把文件顶部 import 替换为：

```python
from dongxuan_agent.calendar_engine import get_calendar_info, with_hour_branch
from .chart import DaliurenChart, build_chart_from_calendar
from dongxuan_agent.constants import BRANCHES, JIAZI
```

在 `dongxuan_agent/daliuren/render.py`, 把文件顶部 import 替换为：

```python
from .chart import DaliurenChart
from .divination import DaliurenDivination
```

在 `dongxuan_agent/daliuren/cli.py`, 把文件顶部 import 替换为：

```python
from .chart import build_chart
from .divination import build_divination
from .render import chart_to_json, divination_to_json, render_chart_markdown, render_divination_markdown
```

在 `dongxuan_agent/daliuren/spirits.py`, 把文件顶部 import 替换为：

```python
from dongxuan_agent.calendar_engine import CalendarInfo
from dongxuan_agent.constants import (
    BRANCH_ELEMENTS,
    BRANCHES,
    DAY_NOBLEMAN,
    HEAVENLY_GENERALS,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
)
from dongxuan_agent.season import season_state
from .transmissions import Transmissions
```

在 `dongxuan_agent/daliuren/transmissions.py`, 把文件顶部 import 替换为：

```python
from dongxuan_agent.constants import (
    BRANCHES,
    CONTROLLING,
    GENERATING,
    STEM_ELEMENTS,
)
```

- [ ] **步骤 5: 更新应用和八字引用**

在 `dongxuan_agent/apps/sessions/daliuren.py`, 把大六壬 import 替换为：

```python
from dongxuan_agent.daliuren.chart import build_chart
from dongxuan_agent.daliuren.divination import build_divination
from dongxuan_agent.daliuren.knowledge import build_daliuren_knowledge_context, render_daliuren_knowledge_markdown
from dongxuan_agent.daliuren.render import chart_to_json, divination_to_json, render_chart_markdown, render_divination_markdown
from dongxuan_agent.daliuren.rule_cards import build_rule_context
```

在 `dongxuan_agent/web/services.py`, 把大六壬 import 替换为：

```python
from dongxuan_agent.daliuren.chart import build_chart
from dongxuan_agent.daliuren.divination import build_divination
from dongxuan_agent.daliuren.knowledge import build_daliuren_knowledge_context
from dongxuan_agent.daliuren.render import chart_to_json, divination_to_json
from dongxuan_agent.daliuren.rule_cards import build_rule_context
```

在 `dongxuan_agent/bazi/year.py` 中，把下面内容替换为：

```python
from ..divination import year_ganzhi
```

为:

```python
from ..daliuren.divination import year_ganzhi
```

- [ ] **步骤 6: 更新 console script**

在 `pyproject.toml` 中，把下面内容替换为：

```toml
daliuren-chart = "dongxuan_agent.cli:main"
```

为:

```toml
daliuren-chart = "dongxuan_agent.daliuren.cli:main"
```

- [ ] **步骤 7: 验证大六壬迁移**

运行:

```bash
uv run pytest tests/test_cli.py tests/test_chart.py tests/test_render.py tests/test_rule_cards.py tests/test_session.py tests/test_web_app.py tests/test_bazi_analysis.py tests/test_bazi_session.py -q
```

预期: PASS。

- [ ] **步骤 8: 确认包顶层大六壬旧路径不再被引用**

运行:

```bash
rg -n "dongxuan_agent\\.(cli|chart|divination|render|rule_cards|daliuren_knowledge)" tests dongxuan_agent tools pyproject.toml
```

预期: 无匹配.

- [ ] **步骤 9: 提交**

运行:

```bash
git add pyproject.toml dongxuan_agent tests
git commit -m "refactor: move daliuren domain into package"
```

---

### 任务 5: 迁移共享基础层到 `dongxuan_agent/core/`

**文件：**
- 新建: `dongxuan_agent/core/__init__.py`
- 移动: `dongxuan_agent/calendar_engine.py` -> `dongxuan_agent/core/calendar_engine.py`
- 移动: `dongxuan_agent/constants.py` -> `dongxuan_agent/core/constants.py`
- 移动: `dongxuan_agent/season.py` -> `dongxuan_agent/core/season.py`
- 移动: `dongxuan_agent/xun.py` -> `dongxuan_agent/core/xun.py`
- 修改: `dongxuan_agent/bazi/chart.py`
- 修改: `dongxuan_agent/bazi/year.py`
- 修改: `dongxuan_agent/bazi/strength.py`
- 修改: `dongxuan_agent/bazi/spirits.py`
- 修改: `dongxuan_agent/bazi/luck_remedy.py`
- 修改: `dongxuan_agent/bazi/integration.py`
- 修改: `dongxuan_agent/liuyao/chart.py`
- 修改: `dongxuan_agent/daliuren/chart.py`
- 修改: `dongxuan_agent/daliuren/divination.py`
- 修改: `dongxuan_agent/daliuren/spirits.py`
- 修改: `dongxuan_agent/daliuren/transmissions.py`
- 修改: `tests/test_calendar_engine.py`

- [ ] **步骤 1: 更新 calendar 测试为 canonical core 路径**

在 `tests/test_calendar_engine.py` 中，把下面内容替换为：

```python
from dongxuan_agent.calendar_engine import (
```

为:

```python
from dongxuan_agent.core.calendar_engine import (
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_calendar_engine.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'dongxuan_agent.core'`。

- [ ] **步骤 3: 移动 core 文件**

运行:

```bash
mkdir -p dongxuan_agent/core
git mv dongxuan_agent/calendar_engine.py dongxuan_agent/core/calendar_engine.py
git mv dongxuan_agent/constants.py dongxuan_agent/core/constants.py
git mv dongxuan_agent/season.py dongxuan_agent/core/season.py
git mv dongxuan_agent/xun.py dongxuan_agent/core/xun.py
```

创建 `dongxuan_agent/core/__init__.py`:

```python
"""Shared calendar and metaphysics foundations."""
```

- [ ] **步骤 4: 更新 core 内部 import**

在 `dongxuan_agent/core/calendar_engine.py` 中，把下面内容替换为：

```python
from .constants import BRANCHES, JIAZI, STEMS, ZHONGQI_MONTH_GENERAL
```

为:

```python
from .constants import BRANCHES, JIAZI, STEMS, ZHONGQI_MONTH_GENERAL
```

这一行保持不变，因为 `calendar_engine.py` 和 `constants.py` 会一起迁到 `core`。

在 `dongxuan_agent/core/season.py` 中，把下面内容替换为：

```python
from .constants import BRANCH_ELEMENTS, GENERATING
```

为:

```python
from .constants import BRANCH_ELEMENTS, GENERATING
```

这一行保持不变，因为 `season.py` 和 `constants.py` 会一起迁到 `core`。

在 `dongxuan_agent/core/xun.py` 中，把下面内容替换为：

```python
from .constants import BRANCHES, JIAZI, STEMS
```

为:

```python
from .constants import BRANCHES, JIAZI, STEMS
```

这一行保持不变，因为 `xun.py` 和 `constants.py` 会一起迁到 `core`。

- [ ] **步骤 5: 更新领域模块 import**

Apply these exact replacements:

```text
from ..calendar_engine import
-> from ..core.calendar_engine import

from ..constants import
-> from ..core.constants import

from dongxuan_agent.calendar_engine import
-> from dongxuan_agent.core.calendar_engine import

from dongxuan_agent.constants import
-> from dongxuan_agent.core.constants import

from dongxuan_agent.season import
-> from dongxuan_agent.core.season import

from dongxuan_agent.xun import
-> from dongxuan_agent.core.xun import
```

在 `dongxuan_agent/daliuren/chart.py`, imports should include:

```python
from dongxuan_agent.core.calendar_engine import CalendarInfo, get_calendar_info
from dongxuan_agent.core.constants import (
    BRANCH_ELEMENTS,
    BRANCHES,
    CONTROLLING,
    DAY_NOBLEMAN,
    GENERATING,
    HEAVENLY_GENERALS,
    HEAVENLY_OFFICER_NAMES,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
)
from dongxuan_agent.core.season import season_state
from dongxuan_agent.core.xun import build_xun_dun
```

在 `dongxuan_agent/daliuren/divination.py`, imports should include:

```python
from dongxuan_agent.core.calendar_engine import get_calendar_info, with_hour_branch
from dongxuan_agent.core.constants import BRANCHES, JIAZI
```

在 `dongxuan_agent/bazi/chart.py`, imports should include:

```python
from ..core.calendar_engine import CalendarInfo, get_calendar_info, hour_gz_by_branch, parse_datetime, xunkong_for_day
from ..core.constants import (
```

在 `dongxuan_agent/liuyao/chart.py`, imports should include:

```python
from ..core.calendar_engine import CalendarInfo, get_calendar_info
```

- [ ] **步骤 6: 验证 core 迁移**

运行:

```bash
uv run pytest tests/test_calendar_engine.py tests/test_chart.py tests/test_render.py tests/test_cli.py tests/test_bazi.py tests/test_bazi_context.py tests/test_liuyao_chart.py tests/test_web_app.py -q
```

预期: PASS。

- [ ] **步骤 7: 确认旧 core 路径不再被引用**

运行:

```bash
rg -n "dongxuan_agent\\.(calendar_engine|constants|season|xun)|from \\.calendar_engine|from \\.constants|from \\.season|from \\.xun|from \\.\\.calendar_engine|from \\.\\.constants" dongxuan_agent tests
```

预期: 无匹配.

- [ ] **步骤 8: 提交**

运行:

```bash
git add dongxuan_agent tests/test_calendar_engine.py
git commit -m "refactor: move shared foundations into core package"
```

---

### 任务 6: 迁移 tools wrapper 并保留根目录兼容入口

**文件：**
- 新建: `tools/__init__.py`
- 新建: `tools/bazi/__init__.py`
- 新建: `tools/daliuren/__init__.py`
- 新建: `tools/liuyao/__init__.py`
- 移动: `tools_bazi_chart_wrapper.py` -> `tools/bazi/chart_wrapper.py`
- 移动: `tools_bazi_session_wrapper.py` -> `tools/bazi/session_wrapper.py`
- 移动: `tools_daliuren_chart_wrapper.py` -> `tools/daliuren/chart_wrapper.py`
- 移动: `tools_daliuren_session_wrapper.py` -> `tools/daliuren/session_wrapper.py`
- 移动: `tools_liuyao_chart_wrapper.py` -> `tools/liuyao/chart_wrapper.py`
- 移动: `tools_liuyao_session_wrapper.py` -> `tools/liuyao/session_wrapper.py`
- 新建: 保持原文件名的根目录 wrapper 文件
- 新建: `tests/test_tool_wrappers.py`

- [ ] **步骤 1: 写工具 wrapper 入口测试**

创建 `tests/test_tool_wrappers.py`:

```python
import importlib


def test_root_tool_wrappers_delegate_to_canonical_modules():
    mappings = {
        "tools_bazi_chart_wrapper": "tools.bazi.chart_wrapper",
        "tools_bazi_session_wrapper": "tools.bazi.session_wrapper",
        "tools_daliuren_chart_wrapper": "tools.daliuren.chart_wrapper",
        "tools_daliuren_session_wrapper": "tools.daliuren.session_wrapper",
        "tools_liuyao_chart_wrapper": "tools.liuyao.chart_wrapper",
        "tools_liuyao_session_wrapper": "tools.liuyao.session_wrapper",
    }
    for root_module_name, canonical_module_name in mappings.items():
        root_module = importlib.import_module(root_module_name)
        canonical_module = importlib.import_module(canonical_module_name)
        assert root_module.main is canonical_module.main
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_tool_wrappers.py -q
```

预期: FAIL，错误包含 `ModuleNotFoundError: No module named 'tools.bazi'`。

- [ ] **步骤 3: 移动工具 wrapper**

运行:

```bash
mkdir -p tools/bazi tools/daliuren tools/liuyao
git mv tools_bazi_chart_wrapper.py tools/bazi/chart_wrapper.py
git mv tools_bazi_session_wrapper.py tools/bazi/session_wrapper.py
git mv tools_daliuren_chart_wrapper.py tools/daliuren/chart_wrapper.py
git mv tools_daliuren_session_wrapper.py tools/daliuren/session_wrapper.py
git mv tools_liuyao_chart_wrapper.py tools/liuyao/chart_wrapper.py
git mv tools_liuyao_session_wrapper.py tools/liuyao/session_wrapper.py
```

创建 `tools/__init__.py`:

```python
"""External tool wrappers."""
```

创建 `tools/bazi/__init__.py`:

```python
"""Bazi tool wrappers."""
```

创建 `tools/daliuren/__init__.py`:

```python
"""Daliuren tool wrappers."""
```

创建 `tools/liuyao/__init__.py`:

```python
"""Liuyao tool wrappers."""
```

- [ ] **步骤 4: 替换 canonical wrapper 实现**

设置 `tools/bazi/chart_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.bazi.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

设置 `tools/bazi/session_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.bazi import main


if __name__ == "__main__":
    raise SystemExit(main())
```

设置 `tools/daliuren/chart_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.daliuren.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

设置 `tools/daliuren/session_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.daliuren import main


if __name__ == "__main__":
    raise SystemExit(main())
```

设置 `tools/liuyao/chart_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.liuyao.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

设置 `tools/liuyao/session_wrapper.py` to:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dongxuan_agent.apps.sessions.liuyao import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **步骤 5: 创建根目录兼容 wrapper**

创建 `tools_bazi_chart_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.bazi.chart_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `tools_bazi_session_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.bazi.session_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `tools_daliuren_chart_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.daliuren.chart_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `tools_daliuren_session_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.daliuren.session_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `tools_liuyao_chart_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.liuyao.chart_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

创建 `tools_liuyao_session_wrapper.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from tools.liuyao.session_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **步骤 6: 验证 tools wrapper**

运行:

```bash
uv run pytest tests/test_tool_wrappers.py tests/test_bazi_cli.py tests/test_cli.py tests/test_liuyao_cli.py tests/test_bazi_session.py tests/test_session.py tests/test_liuyao_session.py -q
```

预期: PASS。

- [ ] **步骤 7: 清理空工具目录**

运行:

```bash
find tools -type d -empty -print
```

预期: 不输出 `tools/allUse`。如果输出 `tools/allUse`，执行阶段需要先确认该目录为空，再删除该空目录。

- [ ] **步骤 8: 提交**

运行:

```bash
git add tools tools_bazi_chart_wrapper.py tools_bazi_session_wrapper.py tools_daliuren_chart_wrapper.py tools_daliuren_session_wrapper.py tools_liuyao_chart_wrapper.py tools_liuyao_session_wrapper.py tests/test_tool_wrappers.py
git commit -m "refactor: organize tool wrappers by domain"
```

---

### 任务 7: 更新运行数据默认位置和中文文档

**文件：**
- 修改: `.gitignore`
- 修改: `dongxuan_agent/web/config.py`
- 修改: `tests/test_web_app.py`
- 修改: `tests/test_web_memory.py`
- 修改: `tests/test_docker_config.py`
- 修改: `docs/docker-web.md`
- 新建: `data/samples/.gitkeep`

- [ ] **步骤 1: 更新运行数据路径测试**

在 `tests/test_web_app.py` 中，把期待 `.dongxuan` 默认父目录的断言改为期待 `data/runtime`。

在检查默认 settings 路径的位置使用这个断言：

```python
assert paths[0].parent == Path(__file__).resolve().parents[1] / "data" / "runtime"
```

在 `tests/test_web_memory.py` 中，创建临时 store 的测试继续使用 `tmp_path`，不要断言 `.dongxuan`。

在 `tests/test_docker_config.py` 中，保留 Docker volume 断言：

```python
assert "./dongxuan-data:/data/dongxuan" in compose
```

新增这个断言，确认文档写明本地默认路径：

```python
assert "data/runtime" in Path("docs/docker-web.md").read_text(encoding="utf-8")
```

- [ ] **步骤 2: 运行测试确认失败**

运行:

```bash
uv run pytest tests/test_web_app.py tests/test_web_memory.py tests/test_docker_config.py -q
```

预期: FAIL，至少一个断言仍看到 `.dongxuan` 默认路径或文档缺少 `data/runtime`。

- [ ] **步骤 3: 更新 `.gitignore`**

追加：

```gitignore
data/runtime/
```

保留已有条目：

```gitignore
.dongxuan/
dongxuan-data/
```

- [ ] **步骤 4: 更新 Web 默认配置**

在 `dongxuan_agent/web/config.py` 中，新增：

```python
DEFAULT_RUNTIME_DIR = PROJECT_ROOT / "data" / "runtime"
```

把 dataclass 默认值替换为：

```python
    memory_path: Path = DEFAULT_RUNTIME_DIR / "memory.json"
    audit_log_path: Path = DEFAULT_RUNTIME_DIR / "audit.jsonl"
```

替换:

```python
memory_path = Path(os.getenv("DONGXUAN_MEMORY_PATH", str(PROJECT_ROOT / ".dongxuan" / "memory.json"))).expanduser()
```

为:

```python
memory_path = Path(os.getenv("DONGXUAN_MEMORY_PATH", str(DEFAULT_RUNTIME_DIR / "memory.json"))).expanduser()
```

保持 `_candidate_auth_paths()` 和 `_candidate_config_path()` 使用 `.dongxuan`，用于兼容 Codex auth/config。除非用户明确要求迁移这些密钥配置，否则不要改动它们。

- [ ] **步骤 5: 创建可提交的数据样例目录占位**

运行:

```bash
mkdir -p data/samples
touch data/samples/.gitkeep
```

不要在 `data/runtime/` 下创建会被 git 跟踪的文件。

- [ ] **步骤 6: 重写 Docker Web 文档为中文**

把 `docs/docker-web.md` 替换为：

````markdown
# Docker Web 运行说明

## 本地环境

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env`，填写 `OPENAI_API_KEY`。

默认 OpenAI 兼容配置：

```env
OPENAI_BASE_URL=https://aivalux.com
OPENAI_MODEL=gpt-5.5
OPENAI_WIRE_API=responses
```

## 启动服务

```bash
docker compose up --build
```

Web UI 默认监听：

```text
http://localhost:8000
```

## 运行数据

本地 Python 运行默认使用：

```text
data/runtime/
```

Docker 运行为了兼容已有部署，仍挂载：

```text
./dongxuan-data:/data/dongxuan
```

`dongxuan-data/memory.json` 保存案例记忆，`dongxuan-data/audit.jsonl` 保存审计日志。审计日志记录密码指纹、动作名、案例 ID 和状态，不记录明文密码。

`.dongxuan/` 是历史本地运行目录，仍可作为 Codex auth/config 兼容位置。

## Cloudflared 提示

如果网络阻断 HTTP/2 over TCP，但允许 QUIC，可以显式使用 QUIC：

```bash
cloudflared tunnel --protocol quic run dongxuan
```

预检查里 TCP 端口 `7844` 的警告表示 HTTP/2 transport 不可用，不代表 tunnel 不能运行。浏览器刷新或快速切换页面时出现 `stream canceled` 通常是前端取消了旧请求。
````

- [ ] **步骤 7: 验证运行数据和文档**

运行:

```bash
uv run pytest tests/test_web_app.py tests/test_web_memory.py tests/test_docker_config.py -q
```

预期: PASS。

- [ ] **步骤 8: 提交**

运行:

```bash
git add .gitignore data/samples/.gitkeep dongxuan_agent/web/config.py tests/test_web_app.py tests/test_web_memory.py tests/test_docker_config.py docs/docker-web.md
git commit -m "refactor: move local runtime defaults under data"
```

---

### 任务 8: 全仓旧路径清理和完整验证

**文件：**
- 修改: `docs/superpowers/plans/2026-07-06-project-file-organization.md`，仅在执行记录需要更新 checkbox 时修改
- 修改: `rg` 找出的 active source 或测试文件

- [ ] **步骤 1: 检查根目录不再有 prompt 文件**

运行:

```bash
test ! -e bazi_prompt.md
test ! -e daliuren_prompt.md
test ! -e liuyao_prompt.md
```

预期: 命令退出码为 0.

- [ ] **步骤 2: 检查包顶层旧领域文件不存在**

运行:

```bash
test ! -e dongxuan_agent/cli.py
test ! -e dongxuan_agent/bazi_cli.py
test ! -e dongxuan_agent/liuyao_cli.py
test ! -e dongxuan_agent/bazi_analysis.py
test ! -e dongxuan_agent/bazi_climate.py
test ! -e dongxuan_agent/bazi_god.py
test ! -e dongxuan_agent/bazi_imagery.py
test ! -e dongxuan_agent/bazi_integration.py
test ! -e dongxuan_agent/bazi_luck_remedy.py
test ! -e dongxuan_agent/bazi_pattern.py
test ! -e dongxuan_agent/bazi_remedy.py
test ! -e dongxuan_agent/bazi_rule_cards.py
test ! -e dongxuan_agent/bazi_strength.py
```

预期: 命令退出码为 0.

- [ ] **步骤 3: 检查 active source 和 tests 没有旧路径引用**

运行:

```bash
rg -n "dongxuan_agent\\.(cli|bazi_cli|liuyao_cli|bazi_analysis|bazi_climate|bazi_god|bazi_imagery|bazi_integration|bazi_luck_remedy|bazi_pattern|bazi_remedy|bazi_rule_cards|bazi_strength|chart|divination|render|rule_cards|daliuren_knowledge|calendar_engine|constants|season|xun)" dongxuan_agent tests tools pyproject.toml
```

预期: 无匹配.

- [ ] **步骤 4: 允许旧路径只出现在历史文档**

运行:

```bash
rg -n "dongxuan_agent\\.(bazi_cli|liuyao_cli|bazi_analysis|chart|divination)|bazi_prompt.md|daliuren_prompt.md|liuyao_prompt.md" docs/superpowers/specs docs/superpowers/plans
```

预期: 匹配只出现在历史设计文档、历史计划文档，或本计划的迁移说明中。

- [ ] **步骤 5: 运行聚焦测试**

运行:

```bash
uv run pytest tests/test_prompt_resolver.py tests/test_session_entrypoints.py tests/test_tool_wrappers.py tests/test_bazi_cli.py tests/test_liuyao_cli.py tests/test_cli.py tests/test_bazi_session.py tests/test_session.py tests/test_liuyao_session.py tests/test_web_app.py tests/test_docker_config.py -q
```

预期: PASS。

- [ ] **步骤 6: 运行完整测试**

运行:

```bash
uv run pytest
```

预期: PASS。

- [ ] **步骤 7: 查看工作区状态**

运行:

```bash
git status --short
```

预期: 只显示本次任务有意修改或新增的文件。既有未跟踪 `.superpowers/` 可以继续保持未提交状态。

- [ ] **步骤 8: 最终提交**

运行:

```bash
git add docs/superpowers/plans/2026-07-06-project-file-organization.md
git commit -m "docs: record file organization verification"
```

预期: 如果执行过程更新了本计划的 checkbox 或验证记录，则提交成功。如果本计划没有变更，跳过最终提交，并记录“无需最终提交”。不要使用 `git add .`，避免把既有未跟踪 `.superpowers/` 纳入提交。

---

## 自查清单

- 设计规格要求的 `prompts/`、`tools/<domain>/`、`dongxuan_agent/apps/sessions/`、`dongxuan_agent/daliuren/`、`dongxuan_agent/core/` 都有任务覆盖。
- 包顶层旧领域入口不保留，任务 3、任务 4、任务 5、任务 8 都有清理和 `rg` 验证。
- 项目根目录外部入口 wrapper 保留，任务 2 和任务 6 有测试覆盖。
- 本地运行数据默认路径改为 `data/runtime/`，Docker 的 `dongxuan-data` 兼容挂载保留，任务 7 有测试和中文文档覆盖。
- 计划文档使用中文；代码标识符、路径和命令保持原文。
