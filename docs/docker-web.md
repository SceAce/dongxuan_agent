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

Audit logs are written to `./dongxuan-data/audit.jsonl`. The log stores password fingerprints, action names, case IDs, and status; it does not store plaintext passwords.

For a Cloudflared named tunnel on networks where HTTP/2 over TCP is blocked but QUIC passes, run the tunnel with QUIC explicitly:

```bash
cloudflared tunnel --protocol quic run dongxuan
```

The pre-check warning about TCP port `7844` means HTTP/2 transport is unavailable, not that the tunnel is unusable. If QUIC is registered, the service can continue. Repeated `stream canceled` lines often happen when the browser cancels in-flight requests during refreshes or rapid UI changes.
