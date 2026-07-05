#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from dongxuan_agent.apps.prompts import read_prompt
from dongxuan_agent.liuyao.context import build_liuyao_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成供 Codex 分析的六爻上下文。")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lines", help="六次摇卦结果，自下而上。")
    mode.add_argument("--hexagram", help="命名卦，例如：离之大有。")
    mode.add_argument("--random", action="store_true", help="按三枚铜钱概率随机生成六爻。")
    parser.add_argument("--datetime", help="起卦时间；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--question")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--include-prompt", action="store_true")
    args = parser.parse_args(argv)

    payload = build_liuyao_context(
        lines=args.lines,
        hexagram=args.hexagram,
        random_lines=args.random,
        seed=args.seed,
        question=args.question,
        value=args.datetime,
        timezone=args.timezone,
    )
    if args.include_prompt:
        print(read_prompt("liuyao").strip())
        print("\n---\n")
    print("## 六爻工具上下文\n")
    print("将下面 JSON 作为唯一六爻排盘与分析提示依据；不要脱离字段自由发挥。\n")
    print("```json")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
