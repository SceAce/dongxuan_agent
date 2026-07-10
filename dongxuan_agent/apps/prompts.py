from __future__ import annotations

from importlib.resources import files
from typing import Literal


PromptName = Literal["bazi", "daliuren", "liuyao"]

PROMPT_PACKAGE = "dongxuan_agent.resources.prompts"
PROMPT_FILES: dict[PromptName, str] = {
    "bazi": "bazi.md",
    "daliuren": "daliuren.md",
    "liuyao": "liuyao.md",
}


def prompt_label(name: PromptName) -> str:
    return f"dongxuan_agent/resources/prompts/{PROMPT_FILES[name]}"


def read_prompt(name: PromptName) -> str:
    return files(PROMPT_PACKAGE).joinpath(PROMPT_FILES[name]).read_text(encoding="utf-8")
