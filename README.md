# Dongxuan Agent

东玄术数本地工具集，提供八字和大六壬的排盘、结构化分析上下文与提示词资源。项目只包含本地 CLI 和 Python 会话入口，不包含 Web 服务器、认证、管理后台或容器部署。

## 安装

需要 Python 3.11 或更高版本，并安装 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync --all-groups
```

## 排盘命令

```bash
# 八字
uv run bazi-chart "2006-12-18 12:30:00" --gender 男 --format json

# 大六壬
uv run daliuren-chart "2026-05-26 10:14:15" --mode number --number 9 --question "所问事项" --format json
```

需要完整分析上下文和可选提示词时，使用仓库中的会话入口：

```bash
uv run python bazi_session.py "2006-12-18 12:30:00" --gender 男 --target-year 2025 --question "所问事项" --include-prompt
uv run python daliuren_session.py "2026-05-26 10:14:15" --mode number --number 9 --question "所问事项" --include-prompt
```

## 本地知识库

默认知识库目录为 `/home/source/Documents/东玄知识库/wiki`。可以用环境变量覆盖，变量应指向知识库的 `wiki/` 目录：

```bash
export DONGXUAN_KNOWLEDGE_ROOT=/path/to/knowledge-base/wiki
```

知识库缺失、不可读或结构化 JSON 无效时，输出会在 `availability` 中给出明确状态，并降级为空知识层；序列化结果只暴露相对 `source`，不会暴露本机绝对路径。

## 八字时间规则

- 子时以 `24:00` 为日界：`23:00-23:59` 属当前自然日的晚子时，`00:00-00:59` 属新自然日的早子时。
- `--longitude` 只做经度近似校正：相对时区中央经线每差 1 度折算 4 分钟。
- 经度近似未加入均时差，不应表述为完整真太阳时；未提供经度时不启用校正。

## 质量检查

```bash
uv run ruff check .
uv run mypy dongxuan_agent
uv run pytest -q
uv run python -m compileall -q dongxuan_agent
uv build
```
