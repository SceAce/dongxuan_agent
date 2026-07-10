# 项目审计问题修复设计

## 目标

以本地 `feature/liuyao-tool-mvp` 为完整功能基线，删除不再需要的 Web 与部署能力，修复审计确认的领域边界、知识库可移植性、资源打包和工程质量问题，最终将验证通过的结果整合到 `master`。

## 基线与分支策略

- 从 `feature/liuyao-tool-mvp` 创建隔离分支 `fix/audit-remediation`。
- 所有代码、测试和文档修改先在隔离分支完成。
- 验证通过后，把完整结果整合到本地 `master`，使 `master` 成为唯一主线。
- 不自动推送远端。

## 删除范围

完整删除以下不再使用的能力：

- `dongxuan_agent/web/` 下的 Web API、静态页面、鉴权、管理员、审计和案例存储。
- `Dockerfile`、`docker-compose.yml`、`.dockerignore`、`.env.example`。
- Web 启动脚本和 Docker Web 文档。
- FastAPI、HTTPX、Uvicorn 等只服务于 Web 的依赖。
- Web、Docker、鉴权、审计和案例存储测试。
- 当前主工作区中的 `.env`、`.dongxuan/`、`data/runtime/`、`dongxuan-data/`。

保留八字、大六壬、六爻、命令行工具、Prompt、本地知识库接入和 `sports_betting.py`。未被确认删除的 `.superpowers/` 不处理。

## 八字领域边界

### 早晚子时

项目只保留一套规则，不再提供 `whole/split` 选择：

- `23:00:00` 至 `23:59:59` 属于当天晚子时，日柱使用当天。
- `00:00:00` 至 `00:59:59` 属于次日早子时，日柱使用该自然日。
- 日界为 `24:00`。
- 输出的 `time_rules` 明确记录“早晚子时，以 24:00 为日界”。

删除 CLI、会话入口和库函数中的 `zi_hour_rule` 参数，避免名称与行为再次相反。

### 大运匹配

- `target_year` 早于出生年时抛出清晰的 `ValueError`，不生成年份分析。
- `current_luck` 只在目标年确实落入某步大运区间时返回大运对象。
- 起运前返回 `current_luck: null`，并输出 `luck_status.status: not_started`。
- 超出已生成大运范围时返回 `current_luck: null`，并输出 `luck_status.status: out_of_range`。
- 未提供有效性别、无法生成大运时输出 `luck_status.status: unavailable`。
- 正常匹配时输出 `luck_status.status: matched`。
- 下游综合分析在 `current_luck` 为空时跳过大运层，只保留原局与流年分析，并把原因加入不确定项。

本地知识库索引与原始资料《八字之门》用于核验：大运从计算出的起运时间开始，每步十年；起运前不能回退到最后一步大运。早晚子时规则以用户确认的 24 点日界为最终项目规则。

### 输入校验与规则卡

- 经度必须是有限浮点数且位于 `[-180, 180]`。
- 当前经度算法只称为“经度近似校正”，明确说明未加入均时差，不宣称完整真太阳时。
- 目标年份不再默认附加“学业”和“财务”规则卡；领域卡只由实际问题关键词选择。

## 本地知识库接入

新增统一知识库路径解析模块，八字和大六壬共用：

1. 优先读取 `DONGXUAN_KNOWLEDGE_ROOT`。
2. 未配置时检测 `/home/source/Documents/东玄知识库/wiki`。
3. 路径不存在时返回结构化降级状态，不中断基础排盘。

输出约束：

- 对外上下文只包含相对路径、逻辑来源名和可用状态。
- 不输出 `/home/source/...` 等本机绝对路径。
- 文件不存在、不可读、JSON 损坏分别记录状态和简短原因。
- 缺少知识资料时不生成伪造摘录或象义。
- Prompt 删除写死的本地工具路径，统一引用项目 CLI 与 JSON 上下文。

## 包资源与命令行

- Prompt 移入 Python 包资源目录。
- 使用 `importlib.resources` 读取 Prompt，源码运行和 wheel 安装采用同一路径。
- 增加明确的构建系统与包数据配置，确保 wheel 包含 Prompt。
- 保留现有三个排盘 CLI 和会话入口兼容层；只移除已经废弃的子时参数。
- CLI 对无效领域输入返回可操作错误，不暴露内部绝对路径。

## 工程质量

- 增加 README，说明八字、大六壬、六爻 CLI、知识库配置、早晚子时规则和算法边界。
- 将 Ruff 和 Mypy 纳入开发依赖及 `pyproject.toml` 配置。
- 修复当前静态类型错误，不使用全局忽略掩盖问题。
- 新增 CI，在 Python 3.11 和 3.13 上运行 Ruff、Mypy、Pytest、源码编译和包构建。
- `sports_betting.py` 保持独立库模块，不增加未被需求驱动的 CLI 或 Web 集成。

## 测试策略

所有行为修改采用测试先行：先写最小失败测试并确认失败原因，再实现最小修复。

必须覆盖：

- 仓库不存在 Web、Docker、鉴权、审计和案例存储代码及其依赖。
- 23:00 使用当天日柱，00:00 使用下一自然日日柱。
- 起运前、正常匹配、出生年前、超出范围和无大运五类年份状态。
- 下游综合分析能处理空 `current_luck`。
- 经度边界值、越界值、`NaN` 和无穷值。
- 知识库默认路径、环境变量覆盖、缺失、不可读和损坏数据。
- 输出不包含本机绝对路径。
- 规则卡不再为任意目标年强加学业和财务领域。
- 从 wheel 安装后可读取三个 Prompt 并运行 CLI。

最终验收命令包括 Ruff、Mypy、完整 Pytest、`compileall` 和 `uv build`。

## 数据删除与交付

代码验证完成后，永久删除主工作区中已获授权的 `.env`、`.dongxuan/`、`data/runtime/`、`dongxuan-data/`。删除前只核对路径，不读取或复制凭据内容。

隔离分支全部验收通过后整合到本地 `master`。整合后重新执行完整验收，并确认工作区只剩用户未要求处理的文件。
