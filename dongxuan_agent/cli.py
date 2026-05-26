from __future__ import annotations

import argparse
import json
from datetime import datetime

from .chart import build_chart
from .divination import build_divination
from .render import chart_to_json, divination_to_json, render_chart_markdown, render_divination_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="排大六壬课盘并输出 Markdown 或 JSON。")
    parser.add_argument("datetime", nargs="?", help="起课时间，例如 '2026-05-26 00:09:14'；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="时区，默认 Asia/Shanghai。")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="输出格式。")
    parser.add_argument("--mode", choices=("time", "live-hour", "number"), default="time", help="起课方式。")
    parser.add_argument("--hour-branch", help="活时起课所报/所抽地支。")
    parser.add_argument("--number", type=int, help="报数起课数字。")
    parser.add_argument("--gender", choices=("男", "女"), help="测算必须字段：性别。")
    parser.add_argument("--question", help="测算必须字段：所问事。")
    parser.add_argument("--background", help="当前背景；年运等命理类问题可省略。")
    parser.add_argument("--birth-year", type=int, help="本命出生年份；提供后自动推本命与行年。")
    args = parser.parse_args(argv)

    value = args.datetime or datetime.now().isoformat(timespec="seconds")
    if args.gender or args.question or args.mode != "time" or args.hour_branch or args.number or args.birth_year:
        divination = build_divination(
            value,
            timezone=args.timezone,
            mode=args.mode,
            hour_branch=args.hour_branch,
            number=args.number,
            gender=args.gender or "",
            question=args.question or "",
            background=args.background,
            birth_year=args.birth_year,
        )
        if args.format == "json":
            print(json.dumps(divination_to_json(divination), ensure_ascii=False, indent=2))
        else:
            print(render_divination_markdown(divination))
        return 0

    chart = build_chart(value, timezone=args.timezone)
    if args.format == "json":
        print(json.dumps(chart_to_json(chart), ensure_ascii=False, indent=2))
    else:
        print(render_chart_markdown(chart))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
