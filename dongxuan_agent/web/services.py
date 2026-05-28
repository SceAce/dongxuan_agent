from __future__ import annotations

from pathlib import Path
from typing import Literal

from dongxuan_agent.bazi.context import build_bazi_context
from dongxuan_agent.chart import build_chart
from dongxuan_agent.divination import build_divination
from dongxuan_agent.render import chart_to_json, divination_to_json
from dongxuan_agent.rule_cards import build_rule_context

from .llm import LLMAdapter

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def analyze_bazi(request, adapter: LLMAdapter) -> dict:
    context = build_bazi_context(
        request.datetime,
        timezone=request.timezone,
        gender=request.gender,
        longitude=request.longitude,
        zi_hour_rule=request.zi_hour_rule,
        target_year=request.target_year,
        question=request.question,
    )
    prompt_file = PROJECT_ROOT / "bazi_prompt.md"
    prompt = prompt_file.read_text(encoding="utf-8")
    analysis = adapter.analyze(system="bazi", prompt=prompt, context=context)
    return _response("bazi", context, analysis, prompt_file)


def analyze_daliuren(request, adapter: LLMAdapter) -> dict:
    context = build_daliuren_context(request)
    prompt_file = PROJECT_ROOT / "daliuren_prompt.md"
    prompt = prompt_file.read_text(encoding="utf-8")
    analysis = adapter.analyze(system="daliuren", prompt=prompt, context=context)
    return _response("daliuren", context, analysis, prompt_file)


def build_daliuren_context(request) -> dict:
    if _needs_divination(request):
        divination = build_divination(
            request.datetime,
            timezone=request.timezone,
            mode=request.mode,
            hour_branch=request.hour_branch,
            number=request.number,
            gender=request.gender or "",
            question=request.question or "",
            background=request.background,
            birth_year=request.birth_year,
        )
        context = divination_to_json(divination)
        context["rule_cards"] = build_rule_context(request.question)
        return context

    context = chart_to_json(build_chart(request.datetime, timezone=request.timezone))
    context["rule_cards"] = build_rule_context(None)
    return context


def _needs_divination(request) -> bool:
    return any(
        (
            request.gender,
            request.question,
            request.mode != "time",
            request.hour_branch,
            request.number is not None,
            request.background,
            request.birth_year is not None,
        )
    )


def _response(system: Literal["bazi", "daliuren"], context: dict, analysis: str, prompt_file: Path) -> dict:
    return {
        "system": system,
        "context": context,
        "analysis": analysis,
        "meta": {
            "readonly": True,
            "prompt_file": prompt_file.name,
        },
    }
