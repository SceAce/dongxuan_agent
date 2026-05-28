#!/usr/bin/env bash
set -euo pipefail

HOST="${DONGXUAN_WEB_HOST:-0.0.0.0}"
PORT="${DONGXUAN_WEB_PORT:-8000}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_AUTH_PATH="${DONGXUAN_CODEX_AUTH_PATH:-$PROJECT_ROOT/.dongxuan/auth.json}"
LOCAL_CONFIG_PATH="${DONGXUAN_CODEX_CONFIG_PATH:-$PROJECT_ROOT/.dongxuan/config.toml}"
SOURCE_AUTH_PATH="${DONGXUAN_SOURCE_AUTH_PATH:-$HOME/.codex/auth.json}"
SOURCE_CONFIG_PATH="${DONGXUAN_SOURCE_CONFIG_PATH:-$HOME/.codex/config.toml}"

export DONGXUAN_LLM_PROVIDER="${DONGXUAN_LLM_PROVIDER:-openai}"
export DONGXUAN_CODEX_AUTH_PATH="$LOCAL_AUTH_PATH"
export DONGXUAN_CODEX_CONFIG_PATH="$LOCAL_CONFIG_PATH"

if [[ ! -f "$LOCAL_AUTH_PATH" && -f "$SOURCE_AUTH_PATH" ]]; then
  mkdir -p "$(dirname "$LOCAL_AUTH_PATH")"
  cp "$SOURCE_AUTH_PATH" "$LOCAL_AUTH_PATH"
  chmod 600 "$LOCAL_AUTH_PATH"
  echo "Copied auth config to $LOCAL_AUTH_PATH"
fi

if [[ ! -f "$LOCAL_CONFIG_PATH" && -f "$SOURCE_CONFIG_PATH" ]]; then
  mkdir -p "$(dirname "$LOCAL_CONFIG_PATH")"
  cp "$SOURCE_CONFIG_PATH" "$LOCAL_CONFIG_PATH"
  chmod 600 "$LOCAL_CONFIG_PATH"
  echo "Copied model config to $LOCAL_CONFIG_PATH"
fi

exec uv run uvicorn dongxuan_agent.web.app:app --host "$HOST" --port "$PORT"
