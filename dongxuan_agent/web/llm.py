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
        self._wire_api = settings.openai_wire_api
        self._timeout = settings.request_timeout_seconds
        self._max_output_tokens = settings.max_output_tokens

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
        if self._wire_api == "responses":
            response = self._post_responses(system=system, prompt=prompt, context=context)
        else:
            response = self._post_chat(messages)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = _extract_error_detail(response)
            raise RuntimeError(f"模型接口返回 {response.status_code}: {detail}") from exc
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"模型接口读取超时，请稍后重试或调大 DONGXUAN_REQUEST_TIMEOUT_SECONDS；当前超时为 {self._timeout} 秒。") from exc
        data = response.json()
        if self._wire_api == "responses":
            return _extract_responses_text(data)
        return _extract_chat_text(data)

    def _post_chat(self, messages: list[dict]) -> httpx.Response:
        return httpx.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            json={
                "model": self._model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": self._max_output_tokens,
            },
            timeout=self._timeout,
        )

    def _post_responses(self, *, system: str, prompt: str, context: dict) -> httpx.Response:
        return httpx.post(
            f"{self._base_url}/responses",
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            json={
                "model": self._model,
                "max_output_tokens": self._max_output_tokens,
                "input": [
                    {
                        "role": "system",
                        "content": "你是只读分析器。只能依据用户消息中的 prompt 与 JSON context 分析，不得要求或假设任何写文件、执行命令、调用 Codex CLI 的能力。",
                    },
                    {
                        "role": "user",
                        "content": _compose_user_message(system=system, prompt=prompt, context=context),
                    },
                ],
            },
            timeout=self._timeout,
        )


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
        "# Output Contract\n"
        "请只按三个 Markdown 模块输出，便于前端渲染成卡片：\n"
        "## 确认前置信息\n"
        "1. 先说明你会按哪个系统流程分析，并校验关键盘面字段。\n"
        "2. 说明输入、盘面、时间、性别、问题语境等前置条件；缺失处只在本模块内简短标明。\n\n"
        "## 分析\n"
        "1. 输出编号化公开分析步骤，逐条列出你引用的 JSON 字段、字段含义、推导方向。\n"
        "2. 每一步必须是可展示给用户的证据链；不要输出隐藏思维链、内部草稿或无字段依据的自由联想。\n\n"
        "3. 如果篇幅不够，优先压缩分析过程，优先保证结论完整。\n\n"
        "## 结论\n"
        "1. 结论必须通俗易懂，像对普通用户解释一样写。\n"
        "2. 少用专有名词，不要堆字段名、神煞名、技术字段名；必须使用术语时，用括号用白话解释。\n"
        "3. 重点回答用户关心的现实问题：大概是什么、偏好还是偏坏、该注意什么、下一步怎么做。\n"
        "4. 给综合判断、主要依据和可行动提醒。\n"
        "5. 不要单列“不确定项”模块；必要的限制和边界只压缩写在结论最后一句。\n\n"
        "# Prompt\n"
        f"{prompt.strip()}\n\n"
        "# JSON Context\n"
        "```json\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        "```"
    )


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:500]
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str):
                return message
        detail = data.get("detail")
        if isinstance(detail, str):
            return detail
    return response.text[:500]


def _extract_chat_text(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("模型接口响应格式不符合 OpenAI chat completions") from exc


def _extract_responses_text(data: dict) -> str:
    text = data.get("output_text")
    if isinstance(text, str) and text:
        return text
    output = data.get("output")
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                part_text = part.get("text")
                if isinstance(part_text, str):
                    chunks.append(part_text)
        if chunks:
            return "\n".join(chunks)
    raise RuntimeError("模型接口响应格式不符合 OpenAI responses")
