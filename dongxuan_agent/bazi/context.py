from __future__ import annotations

from .chart import build_bazi_chart
from .climate import analyze_climate
from .gods import build_god_candidates
from .imagery import build_imagery_analysis
from .integration import build_integrated_analysis
from .luck_remedy import analyze_luck_year_remedy
from .pattern import analyze_pattern
from .remedy import analyze_remedy
from .rule_cards import build_bazi_rule_context
from .strength import analyze_strength
from .year import build_year_analysis_hints


def build_bazi_context(
    value,
    *,
    timezone: str = "Asia/Shanghai",
    gender: str | None = None,
    longitude: float | None = None,
    zi_hour_rule: str = "whole",
    target_year: int | None = None,
    question: str | None = None,
) -> dict:
    chart = build_bazi_chart(
        value,
        timezone=timezone,
        gender=gender,
        longitude=longitude,
        zi_hour_rule=zi_hour_rule,
    )
    payload = chart.to_dict()
    strength_analysis = analyze_strength(chart)
    payload["strength_analysis"] = strength_analysis
    payload["climate_analysis"] = analyze_climate(chart, strength_analysis)
    payload["pattern_analysis"] = analyze_pattern(chart)
    payload["remedy_analysis"] = analyze_remedy(
        payload["strength_analysis"],
        payload["climate_analysis"],
        payload["pattern_analysis"],
    )
    payload["god_candidates"] = build_god_candidates(
        payload["remedy_analysis"],
        payload["strength_analysis"],
        payload["climate_analysis"],
        payload["pattern_analysis"],
    )
    if target_year is not None:
        payload["analysis_hints"] = build_year_analysis_hints(chart, target_year)
        payload["integrated_analysis"] = build_integrated_analysis(
            chart,
            payload["strength_analysis"],
            payload["climate_analysis"],
            payload["analysis_hints"],
        )
        payload["luck_year_remedy"] = analyze_luck_year_remedy(
            chart,
            payload["remedy_analysis"],
            payload["god_candidates"],
            payload["analysis_hints"],
        )
    payload["rule_cards"] = build_bazi_rule_context(question, target_year)
    payload["question"] = question
    payload["imagery_analysis"] = build_imagery_analysis(payload)
    return payload
