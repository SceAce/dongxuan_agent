#!/usr/bin/env bash
set -euo pipefail

HOST="${DONGXUAN_WEB_HOST:-0.0.0.0}"
PORT="${DONGXUAN_WEB_PORT:-8000}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_AUTH_PATH="${DONGXUAN_CODEX_AUTH_PATH:-$PROJECT_ROOT/.dongxuan/auth.json}"
SOURCE_AUTH_PATH="${DONGXUAN_SOURCE_AUTH_PATH:-$HOME/.codex/auth.json}"

export DONGXUAN_LLM_PROVIDER="${DONGXUAN_LLM_PROVIDER:-openai}"
export DONGXUAN_CODEX_AUTH_PATH="$LOCAL_AUTH_PATH"

if [[ ! -f "$LOCAL_AUTH_PATH" && -f "$SOURCE_AUTH_PATH" ]]; then
  mkdir -p "$(dirname "$LOCAL_AUTH_PATH")"
  cp "$SOURCE_AUTH_PATH" "$LOCAL_AUTH_PATH"
  chmod 600 "$LOCAL_AUTH_PATH"
  echo "Copied auth config to $LOCAL_AUTH_PATH"
fi

exec uv run uvicorn dongxuan_agent.web.app:app --host "$HOST" --port "$PORT"
