# Docker Web Runtime

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Edit `.env` and fill `OPENAI_API_KEY`.

The default OpenAI-compatible settings are:

```env
OPENAI_BASE_URL=https://aivalux.com
OPENAI_MODEL=gpt-5.5
OPENAI_WIRE_API=responses
```

3. Start the web service:

```bash
docker compose up --build
```

The web UI listens on `http://localhost:8000` by default. Persistent case memory is stored in `./dongxuan-data/memory.json`.
