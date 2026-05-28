#!/usr/bin/env bash
set -euo pipefail

HOST="${DONGXUAN_WEB_HOST:-0.0.0.0}"
PORT="${DONGXUAN_WEB_PORT:-8000}"

export DONGXUAN_LLM_PROVIDER="${DONGXUAN_LLM_PROVIDER:-openai}"

exec uv run uvicorn dongxuan_agent.web.app:app --host "$HOST" --port "$PORT"
