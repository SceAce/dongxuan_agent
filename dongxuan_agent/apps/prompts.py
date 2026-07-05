from __future__ import annotations

from pathlib import Path
from typing import Literal


PromptName = Literal["bazi", "daliuren", "liuyao"]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = PROJECT_ROOT / "prompts"
PROMPT_FILES: dict[PromptName, str] = {
    "bazi": "bazi.md",
    "daliuren": "daliuren.md",
    "liuyao": "liuyao.md",
}


def prompt_path(name: PromptName) -> Path:
    return PROMPT_DIR / PROMPT_FILES[name]


def prompt_label(name: PromptName) -> str:
    return prompt_path(name).relative_to(PROJECT_ROOT).as_posix()


def read_prompt(name: PromptName) -> str:
    return prompt_path(name).read_text(encoding="utf-8")
