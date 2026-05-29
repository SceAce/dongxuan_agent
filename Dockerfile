FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DONGXUAN_LLM_PROVIDER=echo \
    DONGXUAN_MEMORY_PATH=/data/dongxuan/memory.json

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "dongxuan_agent.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
