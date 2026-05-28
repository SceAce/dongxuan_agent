from __future__ import annotations

import httpx

from .config import WebSettings


class LLMAdapter:
    def analyze(self, *, system: str, prompt: str, context: dict) -> str:
        raise NotImplementedError


class EchoLLMAdapter(LLMAdapter):
    def analyze(self, *, system: str, prompt: str, context: dict) -> str:
        schema = context.get("schema", "unknown")
        question = context.get("question") or context.get("input", {}).get("question") or ""
        return f"echo provider: system={system}, schema={schema}, question={question}, prompt_chars={len(prompt)}"


class OpenAILLMAdapter(LLMAdapter):
    def __init__(self, settings: WebSettings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when DONGXUAN_LLM_PROVIDER=openai")
        self._api_key = settings.openai_api_key
        self._base_url = settings.openai_base_url.rstrip("/")
        self._model = settings.openai_model
        self._timeout = settings.request_timeout_seconds

    def analyze(self, *, system: str, prompt: str, context: dict) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是只读分析器。只能依据用户消息中的 prompt 与 JSON context 分析，不得要求或假设任何写文件、执行命令、调用 Codex CLI 的能力。",
            },
            {
                "role": "user",
                "content": _compose_user_message(system=system, prompt=prompt, context=context),
            },
        ]
        response = httpx.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            json={"model": self._model, "messages": messages, "temperature": 0.2},
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def build_llm_adapter(settings: WebSettings) -> LLMAdapter:
    if settings.llm_provider == "echo":
        return EchoLLMAdapter()
    if settings.llm_provider == "openai":
        return OpenAILLMAdapter(settings)
    raise RuntimeError(f"Unsupported DONGXUAN_LLM_PROVIDER: {settings.llm_provider}")


def _compose_user_message(*, system: str, prompt: str, context: dict) -> str:
    import json

    return (
        f"# System\n{system}\n\n"
        "# Prompt\n"
        f"{prompt.strip()}\n\n"
        "# JSON Context\n"
        "```json\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        "```"
    )
