#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime

from dongxuan_agent.apps.prompts import read_prompt
from dongxuan_agent.bazi.context import build_bazi_context
from dongxuan_agent.bazi.knowledge import build_bazi_knowledge_context


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
    payload = build_bazi_context(
        value,
        timezone=args.timezone,
        gender=args.gender,
        longitude=args.longitude,
        zi_hour_rule=args.zi_hour_rule,
        target_year=args.target_year,
        question=args.question,
    )

    if args.include_prompt:
        print(read_prompt("bazi").strip())
        print("\n---\n")
    print(_knowledge_summary().strip())
    print("\n---\n")
    print("## 八字工具上下文\n")
    print("将下面 JSON 作为唯一八字排盘与分析提示依据；不要脱离字段自由发挥。\n")
    print("```json")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("```")
    return 0


def _knowledge_summary() -> str:
    knowledge = build_bazi_knowledge_context()
    lines = [
        "### 八字知识分层",
        "",
        f"- 层级顺序：{' -> '.join(knowledge['layer_priority'])}",
        f"- 案例偏好：{knowledge['case_policy']['prefer']}",
        "",
        "#### 默认书单",
        "- 理法：" + "；".join(knowledge["book_sets"]["principle"]),
        "- 象法：" + "；".join(knowledge["book_sets"]["symbolic"]),
        "- 案例：" + "；".join(knowledge["book_sets"]["cases"]),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
