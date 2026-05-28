# Readonly Web MVP Design

## Goal

Expose 八字 and 大六壬 analysis through a browser UI while preserving the same chart context and prompt constraints used by terminal sessions. The browser must never get shell, filesystem write, Codex CLI, or arbitrary agent access.

## Architecture

The MVP is a FastAPI app with a static HTML frontend. The frontend collects structured input and sends it to fixed backend endpoints. The backend builds the same JSON contexts used by the terminal tools, combines them with the same local prompt files, and sends the prompt+JSON to a configurable LLM provider adapter. Tests use a fake adapter so the app can be verified without network access.

Request flow:

1. Browser posts JSON to `/api/bazi/analyze` or `/api/daliuren/analyze`.
2. FastAPI validates an optional access password and input length.
3. Backend calls fixed local context builders:
   - 八字: `dongxuan_agent.bazi.context.build_bazi_context`
   - 大六壬: `dongxuan_agent.chart`, `dongxuan_agent.divination`, `dongxuan_agent.render`, `dongxuan_agent.rule_cards`
4. Backend reads the matching prompt file:
   - `bazi_prompt.md`
   - `daliuren_prompt.md`
5. Backend creates a model message that contains the prompt and JSON context as the only analysis source.
6. LLM adapter returns analysis text.
7. API returns `system`, `context`, `analysis`, and metadata to the frontend.

## Security Boundary

The app must be read-only from the user and model perspective.

Allowed:

- Read fixed prompt files.
- Build chart/context JSON through fixed Python functions.
- Send prompt+context to an LLM adapter.
- Return analysis text to the browser.

Forbidden:

- Shell execution from web requests.
- Codex CLI exposure.
- Writing files, commits, generated scripts, or history records.
- Arbitrary file paths supplied by users.
- Arbitrary tool/plugin invocation.
- Model access to secrets beyond the configured API call.

The Docker container should run the app on a single HTTP port and can be mounted read-only by the operator. No Docker socket, privileged mode, or host home mount is required.

## API

### `GET /api/health`

Returns:

```json
{"status": "ok", "systems": ["bazi", "daliuren"]}
```

### `POST /api/bazi/analyze`

Input:

```json
{
  "password": "optional access password",
  "datetime": "2006-12-18 12:30:00",
  "timezone": "Asia/Shanghai",
  "gender": "男",
  "longitude": null,
  "zi_hour_rule": "whole",
  "target_year": 2025,
  "question": "推断2025年发生了什么"
}
```

### `POST /api/daliuren/analyze`

Input:

```json
{
  "password": "optional access password",
  "datetime": "2026-05-28 20:00:00",
  "timezone": "Asia/Shanghai",
  "mode": "time",
  "hour_branch": null,
  "number": null,
  "gender": "男",
  "question": "问工作进展",
  "background": "正在等通知",
  "birth_year": 2000
}
```

Output for both:

```json
{
  "system": "bazi",
  "context": {},
  "analysis": "模型分析文本",
  "meta": {
    "readonly": true,
    "prompt_file": "bazi_prompt.md"
  }
}
```

## LLM Adapter

The app uses `DONGXUAN_LLM_PROVIDER`.

- `echo`: default for local smoke tests; returns a deterministic text and does not use network.
- `openai`: optional production provider; uses `OPENAI_API_KEY`, `OPENAI_MODEL`, and the official OpenAI HTTP API.

The web MVP must work in echo mode without network. Production model calls can be enabled by environment variables after deployment.

## Frontend

The first page is the tool itself, not a landing page. It has tabs for 八字 and 大六壬, compact forms, a submit button, and result panes for analysis and JSON context. It must not show API keys or raw server environment data.

## Verification

Tests must prove:

- Health endpoint works.
- Bazi and Daliuren endpoints build contexts and return analysis with the fake adapter.
- Password enforcement works when configured.
- Question length is bounded.
- Web context generation is semantically equivalent to terminal/session context builders for the same inputs.
- No API endpoint exposes shell/Codex execution.

Smoke verification must start the local server and call `/api/health`, `/api/bazi/analyze`, and `/api/daliuren/analyze` in echo mode.
