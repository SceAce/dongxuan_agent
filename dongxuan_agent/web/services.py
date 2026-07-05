from __future__ import annotations

from typing import Literal

from dongxuan_agent.apps.prompts import prompt_label, read_prompt
from dongxuan_agent.bazi.context import build_bazi_context
from dongxuan_agent.daliuren.chart import build_chart
from dongxuan_agent.daliuren.divination import build_divination
from dongxuan_agent.daliuren.knowledge import build_daliuren_knowledge_context
from dongxuan_agent.daliuren.render import chart_to_json, divination_to_json
from dongxuan_agent.daliuren.rule_cards import build_rule_context

from .llm import LLMAdapter


def analyze_bazi(request, adapter: LLMAdapter, case_memory: dict | None = None) -> dict:
    context = build_bazi_context(
        request.datetime,
        timezone=request.timezone,
        gender=request.gender,
        longitude=request.longitude,
        zi_hour_rule=request.zi_hour_rule,
        target_year=request.target_year,
        question=request.question,
    )
    if case_memory:
        context["case_memory"] = case_memory
    prompt = read_prompt("bazi")
    analysis = adapter.analyze(system="bazi", prompt=prompt, context=context)
    return _response("bazi", context, analysis, prompt_label("bazi"))


def analyze_daliuren(request, adapter: LLMAdapter) -> dict:
    context = build_daliuren_context(request)
    prompt = read_prompt("daliuren")
    analysis = adapter.analyze(system="daliuren", prompt=prompt, context=context)
    return _response("daliuren", context, analysis, prompt_label("daliuren"))


def build_daliuren_context(request) -> dict:
    knowledge = build_daliuren_knowledge_context()
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
        context["knowledge_layers"] = knowledge
        return context

    context = chart_to_json(build_chart(request.datetime, timezone=request.timezone))
    context["rule_cards"] = build_rule_context(None)
    context["knowledge_layers"] = knowledge
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


def _response(system: Literal["bazi", "daliuren"], context: dict, analysis: str, prompt_file: str) -> dict:
    return {
        "system": system,
        "context": context,
        "analysis": analysis,
        "meta": {
            "readonly": True,
            "prompt_file": prompt_file,
        },
    }
