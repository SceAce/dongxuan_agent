# Readonly Web MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only browser MVP for 八字 and 大六壬 analysis that preserves terminal context generation.

**Architecture:** Add a small FastAPI app under `dongxuan_agent/web/`. API routes call fixed local context builders, read fixed prompt files, and use a pluggable LLM adapter. Static frontend lives in `dongxuan_agent/web/static/`.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, uvicorn, pytest, Docker.

---

## File Structure

- Create `dongxuan_agent/web/__init__.py`: package marker.
- Create `dongxuan_agent/web/config.py`: environment-backed settings.
- Create `dongxuan_agent/web/llm.py`: echo and OpenAI-compatible adapters.
- Create `dongxuan_agent/web/services.py`: build bazi/daliuren contexts and model prompts.
- Create `dongxuan_agent/web/app.py`: FastAPI app, auth, routes, static frontend.
- Create `dongxuan_agent/web/static/index.html`: browser UI.
- Create `tests/test_web_app.py`: API, auth, and context parity tests.
- Modify `pyproject.toml`: add FastAPI, uvicorn, httpx dependency and `dongxuan-web` script.
- Create `Dockerfile`: production container entrypoint.
- Create `docker-compose.yml`: local deployment defaults.
- Create `.dockerignore`: slim container context.

## Tasks

### Task 1: Web API Contract Tests

**Files:**
- Create: `tests/test_web_app.py`

- [ ] **Step 1:** Write failing tests for health, bazi, daliuren, auth, length bound, and context parity.
- [ ] **Step 2:** Run `uv run pytest tests/test_web_app.py -q` and verify failure because `dongxuan_agent.web` does not exist.

### Task 2: Backend Implementation

**Files:**
- Create: `dongxuan_agent/web/__init__.py`
- Create: `dongxuan_agent/web/config.py`
- Create: `dongxuan_agent/web/llm.py`
- Create: `dongxuan_agent/web/services.py`
- Create: `dongxuan_agent/web/app.py`
- Modify: `pyproject.toml`

- [ ] **Step 1:** Implement settings and auth helpers.
- [ ] **Step 2:** Implement deterministic echo adapter and optional OpenAI adapter.
- [ ] **Step 3:** Implement context builders by reusing existing local functions.
- [ ] **Step 4:** Implement FastAPI endpoints and static serving.
- [ ] **Step 5:** Run `uv run pytest tests/test_web_app.py -q` and verify pass.

### Task 3: Frontend And Container

**Files:**
- Create: `dongxuan_agent/web/static/index.html`
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`

- [ ] **Step 1:** Implement compact browser UI for 八字 and 大六壬.
- [ ] **Step 2:** Add Docker runtime files.
- [ ] **Step 3:** Run web tests and full tests.
- [ ] **Step 4:** Start server in echo mode and smoke-test endpoints.
- [ ] **Step 5:** Commit all files.
