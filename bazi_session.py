#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi_analysis import build_year_analysis_hints
from dongxuan_agent.bazi_climate import analyze_climate
from dongxuan_agent.bazi_god import build_god_candidates
from dongxuan_agent.bazi_imagery import build_imagery_analysis
from dongxuan_agent.bazi_integration import build_integrated_analysis
from dongxuan_agent.bazi_luck_remedy import analyze_luck_year_remedy
from dongxuan_agent.bazi_pattern import analyze_pattern
from dongxuan_agent.bazi_remedy import analyze_remedy
from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context
from dongxuan_agent.bazi_strength import analyze_strength


PROMPT_PATHS = (
    Path(__file__).with_name("BAZI_PROMPT.md"),
    Path(__file__).with_name("bazi_prompt.md"),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成供 Codex 分析的八字上下文。")
    parser.add_argument("datetime", nargs="?", help="出生时间，例如 '2006-12-18 12:30:00'；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--gender", choices=("男", "女"))
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--zi-hour-rule", choices=("whole", "split"), default="whole")
    parser.add_argument("--target-year", type=int)
    parser.add_argument("--question")
    parser.add_argument("--include-prompt", action="store_true")
    args = parser.parse_args(argv)

    value = args.datetime or datetime.now().isoformat(timespec="seconds")
    chart = build_bazi_chart(
        value,
        timezone=args.timezone,
        gender=args.gender,
        longitude=args.longitude,
        zi_hour_rule=args.zi_hour_rule,
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
    if args.target_year is not None:
        payload["analysis_hints"] = build_year_analysis_hints(chart, args.target_year)
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
    payload["rule_cards"] = build_bazi_rule_context(args.question, args.target_year)
    payload["question"] = args.question
    payload["imagery_analysis"] = build_imagery_analysis(payload)

    if args.include_prompt:
        print(_prompt_path().read_text(encoding="utf-8").strip())
        print("\n---\n")
    print("## 八字工具上下文\n")
    print("将下面 JSON 作为唯一八字排盘与分析提示依据；不要脱离字段自由发挥。\n")
    print("```json")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("```")
    return 0


def _prompt_path() -> Path:
    for path in PROMPT_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("未找到 BAZI_PROMPT.md 或 bazi_prompt.md")


if __name__ == "__main__":
    raise SystemExit(main())
