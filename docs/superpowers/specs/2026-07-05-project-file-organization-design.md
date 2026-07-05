# 东玄项目文件整理设计

## 目标

重新整理当前仓库，让文件按职责归类，而不是按历史创建顺序堆在一起。整理完成后，仓库边界应该清晰体现：

- 领域代码：大六壬、八字、六爻
- 共享基础层：历法、常量、渲染辅助、通用术数工具
- 应用入口：排盘 CLI、上下文生成 session、Web 运行时
- 外部工具 wrapper：统一放入 `tools/`
- 提示词资产：统一放入 `prompts/`
- 运行数据：统一放入 `data/runtime/`，并从 git 中排除

本次整理是结构性调整，不改变业务行为。已经存在的外部调用要继续可用，但具体实现移动到新目录后，由兼容入口转调。

## 文档语言约定

从本次整理开始，新增或重写的计划书、设计文档、`README.md`、使用说明、部署说明等说明性文档，默认使用中文。

例外情况只有两类：

- 上游工具、第三方接口或配置字段要求英文。
- 代码标识符、命令、路径、异常名等必须保持原文。

如果后续文档必须使用英文，需要在文档开头说明原因。

## 当前问题

当前项目根目录混放了配置、提示词、session 生成器、工具 wrapper、运行数据和 Python 包代码。主要问题如下：

- `bazi_session.py`、`daliuren_session.py`、`liuyao_session.py` 是应用入口代码，却放在项目根目录。
- `bazi_prompt.md`、`daliuren_prompt.md`、`liuyao_prompt.md` 是提示词资产，也放在项目根目录。
- `tools_*_wrapper.py` 文件在根目录，而新建的 `tools/` 目录基本为空。
- `dongxuan_agent/` 顶层同时包含领域模块和共享基础模块，职责边界不清楚。
- 八字代码已经大部分进入 `dongxuan_agent/bazi/`，但 `dongxuan_agent/bazi_*.py` 仍保留在包顶层作为兼容 shim，导致包顶层被旧路径污染。
- 运行数据分散在 `.dongxuan/` 和 `dongxuan-data/`；其中 `dongxuan-data/` 目前由 root 拥有，本次整理不应直接移动或修改其中已有文件。

## 目标目录结构

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
│   │   ├── prompts.py
│   │   └── sessions/
│   │       ├── bazi.py
│   │       ├── daliuren.py
│   │       └── liuyao.py
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

项目根目录保留以下兼容入口，但文件内容只能是薄包装：

- `bazi_session.py`
- `daliuren_session.py`
- `liuyao_session.py`
- `tools_bazi_chart_wrapper.py`
- `tools_bazi_session_wrapper.py`
- `tools_daliuren_chart_wrapper.py`
- `tools_daliuren_session_wrapper.py`
- `tools_liuyao_chart_wrapper.py`
- `tools_liuyao_session_wrapper.py`

这些兼容文件只负责导入并调用新位置的实现，不再承载业务逻辑。

`dongxuan_agent/` 包顶层不保留旧领域入口。`dongxuan_agent.cli`、`dongxuan_agent.bazi_cli`、`dongxuan_agent.liuyao_cli` 和 `dongxuan_agent.bazi_*` 旧模块应被迁移或删除，项目内部测试和工具 wrapper 统一改用 canonical 路径。

## 模块迁移设计

### 共享基础层

把通用基础模块迁到 `dongxuan_agent/core/`：

- `calendar_engine.py`
- `constants.py`
- `season.py`
- `xun.py`

`render.py` 需要谨慎拆分。大六壬专用渲染函数迁到 `dongxuan_agent/daliuren/render.py`；只有真正跨领域复用的渲染辅助函数才留在 `core`。

### 大六壬

把当前包顶层的大六壬领域模块迁到 `dongxuan_agent/daliuren/`：

- `chart.py`
- `cli.py`
- `divination.py`
- `daliuren_knowledge.py` 改名为 `knowledge.py`
- `rule_cards.py`
- `spirits.py`
- `transmissions.py`

`pyproject.toml` 中已有的公开命令：

```toml
daliuren-chart = "dongxuan_agent.cli:main"
```

应改为：

```toml
daliuren-chart = "dongxuan_agent.daliuren.cli:main"
```

旧文件 `dongxuan_agent/cli.py` 不保留。测试、工具 wrapper 和文档中的调用统一改为 `dongxuan_agent.daliuren.cli`。

### 八字

现有 `dongxuan_agent/bazi/` 继续作为八字领域代码的 canonical 位置。需要迁移：

- `dongxuan_agent/bazi_cli.py` 迁到 `dongxuan_agent/bazi/cli.py`
- `dongxuan_agent/bazi_knowledge.py` 迁到 `dongxuan_agent/bazi/knowledge.py`

旧文件 `dongxuan_agent/bazi_cli.py` 不保留。`pyproject.toml`、测试和工具 wrapper 统一改为 `dongxuan_agent.bazi.cli`。

当前 `dongxuan_agent/bazi_*.py` 文件不继续保留。这些文件基本只是 3 行 re-export shim，应删除并把测试、内部 import、工具 wrapper 改为 canonical 路径：

- `dongxuan_agent.bazi_analysis` 改为 `dongxuan_agent.bazi.year`
- `dongxuan_agent.bazi_climate` 改为 `dongxuan_agent.bazi.climate`
- `dongxuan_agent.bazi_god` 改为 `dongxuan_agent.bazi.gods`
- `dongxuan_agent.bazi_imagery` 改为 `dongxuan_agent.bazi.imagery`
- `dongxuan_agent.bazi_integration` 改为 `dongxuan_agent.bazi.integration`
- `dongxuan_agent.bazi_luck_remedy` 改为 `dongxuan_agent.bazi.luck_remedy`
- `dongxuan_agent.bazi_pattern` 改为 `dongxuan_agent.bazi.pattern`
- `dongxuan_agent.bazi_remedy` 改为 `dongxuan_agent.bazi.remedy`
- `dongxuan_agent.bazi_rule_cards` 改为 `dongxuan_agent.bazi.rule_cards`
- `dongxuan_agent.bazi_strength` 改为 `dongxuan_agent.bazi.strength`

### 六爻

现有 `dongxuan_agent/liuyao/` 继续作为六爻领域代码的 canonical 位置。需要迁移：

- `dongxuan_agent/liuyao_cli.py` 迁到 `dongxuan_agent/liuyao/cli.py`

旧文件 `dongxuan_agent/liuyao_cli.py` 不保留。测试、工具 wrapper 和文档中的调用统一改为 `dongxuan_agent.liuyao.cli`。

### Session 上下文生成器

把 session/context 生成器迁到 `dongxuan_agent/apps/sessions/`：

- `bazi_session.py` 迁到 `dongxuan_agent/apps/sessions/bazi.py`
- `daliuren_session.py` 迁到 `dongxuan_agent/apps/sessions/daliuren.py`
- `liuyao_session.py` 迁到 `dongxuan_agent/apps/sessions/liuyao.py`

项目根目录的同名文件保留为 wrapper。这样可以保持当前测试和外部调用不变，同时把实现逻辑从根目录移走。

### 提示词

把提示词资产迁到 `prompts/`：

- `bazi_prompt.md` 迁到 `prompts/bazi.md`
- `daliuren_prompt.md` 迁到 `prompts/daliuren.md`
- `liuyao_prompt.md` 迁到 `prompts/liuyao.md`

session 模块和 Web 服务通过 `dongxuan_agent/apps/prompts.py` 统一解析提示词路径，避免以后调整路径时多处修改。

本次整理后，根目录不再保留 prompt 文件副本。提示词策略测试和应用代码都应读取 canonical 的 `prompts/*.md`。

### Tools

把工具 wrapper 实现迁到 `tools/<domain>/`：

- `tools_bazi_chart_wrapper.py` 迁到 `tools/bazi/chart_wrapper.py`
- `tools_bazi_session_wrapper.py` 迁到 `tools/bazi/session_wrapper.py`
- `tools_daliuren_chart_wrapper.py` 迁到 `tools/daliuren/chart_wrapper.py`
- `tools_daliuren_session_wrapper.py` 迁到 `tools/daliuren/session_wrapper.py`
- `tools_liuyao_chart_wrapper.py` 迁到 `tools/liuyao/chart_wrapper.py`
- `tools_liuyao_session_wrapper.py` 迁到 `tools/liuyao/session_wrapper.py`

项目根目录的 wrapper 文件保留为兼容入口。新 wrapper 实现不应继续引用不存在的 `daliuren_agent` 目录，而应直接从当前仓库的 Python 包导入。

### 运行数据

本地运行数据默认使用 `data/runtime/`：

- `data/runtime/memory.json`
- `data/runtime/audit.jsonl`
- `data/runtime/auth.json`
- `data/runtime/config.toml`

Docker 运行继续兼容当前挂载：

```text
./dongxuan-data:/data/dongxuan
```

除非后续明确决定迁移 Docker 数据，否则本次整理不改变 Docker 数据挂载。文档需要说明：

- 本地默认运行数据位置为 `data/runtime/`
- Docker 默认仍使用 `dongxuan-data/`
- `.dongxuan/` 和 `dongxuan-data/` 是历史运行数据位置

不要移动或编辑已有 root-owned 的 `dongxuan-data/` 文件。本次整理只调整默认路径和文档，不碰已有运行状态。

## 兼容策略

兼容 wrapper 必须短小明确，例如：

```python
from __future__ import annotations

from dongxuan_agent.apps.sessions.bazi import main

if __name__ == "__main__":
    raise SystemExit(main())
```

兼容范围只限项目根目录的外部入口 wrapper：

- `bazi_session.py`
- `daliuren_session.py`
- `liuyao_session.py`
- `tools_*_wrapper.py`

`dongxuan_agent/` 包内旧领域路径不再兼容。内部代码、测试、工具 wrapper、`pyproject.toml` 都应改为 canonical 路径；整理完成后用 `rg` 检查旧路径引用已经清空。

## Web 与 Docker 影响

`dongxuan_agent/web/services.py` 应通过新的 prompt resolver 加载提示词。API metadata 应报告 canonical 路径，例如 `prompts/bazi.md` 和 `prompts/daliuren.md`；对应测试也要同步更新。

`dongxuan_agent/web/config.py` 的本地默认运行目录应改为 `data/runtime/`。Docker 环境变量已经覆盖 memory 和 audit 路径，因此容器行为可以保持不变。

移动文件后需要检查 `Dockerfile` 和 `.dockerignore`。由于根目录兼容入口仍保留，Docker build 可以继续复制完整项目。除非测试显示 import 失败，否则不需要改变打包方式。

## 测试策略

本次整理按层验证：

1. 先跑入口相关测试：
   - `tests/test_cli.py`
   - `tests/test_bazi_cli.py`
   - `tests/test_liuyao_cli.py`
   - `tests/test_session.py`
   - `tests/test_bazi_session.py`
   - `tests/test_liuyao_session.py`
2. 移动提示词后跑 prompt policy 测试：
   - `tests/test_prompt_policy.py`
   - `tests/test_bazi_prompt_policy.py`
   - `tests/test_liuyao_prompt_policy.py`
3. 跑 Web 和 Docker 配置测试：
   - `tests/test_web_app.py`
   - `tests/test_web_auth_audit.py`
   - `tests/test_web_memory.py`
   - `tests/test_docker_config.py`
4. 最后跑完整测试：
   - `uv run pytest`
5. 用 `rg` 检查包内旧路径引用已经清空：
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

如果 `uv run pytest` 因依赖下载或网络限制失败，需要按环境权限重新执行，或使用当前已有本地环境完成验证。

## 实施顺序

1. 创建目标目录和统一 prompt resolver。
2. 移动提示词资产，并把测试改为读取 canonical 路径。
3. 移动 session 实现，把根目录 session 文件替换为 wrapper。
4. 移动 tool wrapper 实现到 `tools/<domain>/`，把根目录 wrapper 替换为 wrapper。
5. 移动八字 CLI 和 knowledge 模块到 `dongxuan_agent/bazi/`，删除包顶层旧八字 shim，并更新所有引用。
6. 移动六爻 CLI 到 `dongxuan_agent/liuyao/`，删除包顶层旧六爻 CLI，并更新所有引用。
7. 移动大六壬领域模块到 `dongxuan_agent/daliuren/`，删除包顶层旧大六壬入口，并更新所有引用。
8. 移动共享模块到 `dongxuan_agent/core/`，更新内部 import；只保留项目根目录的外部入口 wrapper。
9. 更新本地运行数据默认路径和 `.gitignore`。
10. 先跑聚焦测试，再跑完整测试。

这个顺序可以让每一步的 import 问题更容易定位。

## 不在本次范围内

- 重写领域算法。
- 改变 CLI 行为或输出格式。
- 删除项目根目录的外部入口兼容 wrapper。
- 迁移已有 root-owned Docker 运行数据。
- 重写旧设计文档或旧计划文档中记录的历史路径。
