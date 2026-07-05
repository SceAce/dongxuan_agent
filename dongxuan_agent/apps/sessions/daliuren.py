#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime

from dongxuan_agent.apps.prompts import read_prompt
from dongxuan_agent.daliuren.chart import build_chart
from dongxuan_agent.daliuren.divination import build_divination
from dongxuan_agent.daliuren.knowledge import build_daliuren_knowledge_context, render_daliuren_knowledge_markdown
from dongxuan_agent.daliuren.render import chart_to_json, divination_to_json, render_chart_markdown, render_divination_markdown
from dongxuan_agent.daliuren.rule_cards import build_rule_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成供 Codex 分析的大六壬测算上下文。")
    parser.add_argument("datetime", nargs="?", help="起课时间，例如 '2026-05-26 10:14:15'；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="时区，默认 Asia/Shanghai。")
    parser.add_argument("--mode", choices=("time", "live-hour", "number"), default="time", help="起课方式。")
    parser.add_argument("--hour-branch", help="活时起课所报/所抽地支。")
    parser.add_argument("--number", type=int, help="报数起课数字。")
    parser.add_argument("--gender", choices=("男", "女"), help="性别；需要行年时用于男女顺逆。")
    parser.add_argument("--question", help="测算必须字段：所问事。")
    parser.add_argument("--background", help="当前背景；年运等命理类问题可省略。")
    parser.add_argument("--birth-year", type=int, help="本命出生年份；提供后自动推本命与行年。")
    parser.add_argument("--include-prompt", action="store_true", help="同时输出大六壬测算 Prompt。")
    args = parser.parse_args(argv)

    value = args.datetime or datetime.now().isoformat(timespec="seconds")
    payload, rendered_chart = _build_payload(args, value)

    if args.include_prompt:
        print(read_prompt("daliuren").strip())
        print("\n---\n")
    print(render_daliuren_knowledge_markdown().strip())
    print("\n---\n")
    print(rendered_chart.strip())
    print("\n---\n")
    print("## 大六壬工具上下文\n")
    print("将下面 JSON 作为唯一课盘依据；分析时按 prompt 结构输出，不要脱离字段自由发挥。\n")
    print("```json")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("```")
    return 0


def _build_payload(args: argparse.Namespace, value: str) -> tuple[dict, str]:
    needs_divination = any((
        args.gender,
        args.question,
        args.mode != "time",
        args.hour_branch,
        args.number is not None,
        args.background,
        args.birth_year is not None,
    ))
    if not needs_divination:
        chart = build_chart(value, timezone=args.timezone)
        payload = chart_to_json(chart)
        payload["rule_cards"] = build_rule_context(None)
        payload["knowledge_layers"] = build_daliuren_knowledge_context()
        return payload, render_chart_markdown(chart)

    divination = build_divination(
        value,
        timezone=args.timezone,
        mode=args.mode,
        hour_branch=args.hour_branch,
        number=args.number,
        gender=args.gender,
        question=args.question or "",
        background=args.background,
        birth_year=args.birth_year,
    )
    payload = divination_to_json(divination)
    payload["rule_cards"] = build_rule_context(args.question)
    payload["knowledge_layers"] = build_daliuren_knowledge_context()
    return payload, render_divination_markdown(divination)


if __name__ == "__main__":
    raise SystemExit(main())
