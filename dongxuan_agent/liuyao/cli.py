from __future__ import annotations

import argparse
import json

from .chart import LiuyaoChart, build_liuyao_chart


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成六爻排盘并输出 Markdown 或 JSON。")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lines", help="六次摇卦结果，自下而上，例如：少阳 老阴 少阴 少阳 老阳 少阴。")
    mode.add_argument("--hexagram", help="命名卦，例如：离之大有、离为火之火天大有。")
    mode.add_argument("--random", action="store_true", help="按三枚铜钱概率随机生成六爻。")
    parser.add_argument("--datetime", help="起卦时间；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="时区，默认 Asia/Shanghai。")
    parser.add_argument("--question", help="所问事项。")
    parser.add_argument("--seed", type=int, help="随机起卦种子，主要用于测试或复现。")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="输出格式。")
    args = parser.parse_args(argv)

    chart = build_liuyao_chart(
        lines=args.lines,
        hexagram=args.hexagram,
        random_lines=args.random,
        seed=args.seed,
        question=args.question,
        value=args.datetime,
        timezone=args.timezone,
    )
    if args.format == "json":
        print(json.dumps(chart.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_liuyao_markdown(chart))
    return 0


def render_liuyao_markdown(chart: LiuyaoChart) -> str:
    payload = chart.to_dict()
    line_rows = "\n".join(
        f"| {line['name']} | {line['input_state']} | {line['yin_yang']} | "
        f"{'是' if line['moving'] else '否'} | {line['changed_yin_yang']} |"
        for line in payload["lines"]
    )
    candidates = "、".join(
        item["six_relative"] for item in payload["question_context"]["candidate_useful_gods"]
    ) or "未分类"
    return f"""## 六爻排盘

- 起卦方式：{payload['input']['method']}
- 所问事项：{payload['input']['question'] or '未提供'}
- 时间：{payload['calendar']['datetime']}
- 本卦：{payload['hexagram']['original']['name']}
- 变卦：{payload['hexagram']['changed']['name']}
- 动爻：{'、'.join(str(item) for item in payload['hexagram']['moving_lines']) or '无'}
- 卦宫：{payload['palace']['palace']}（{payload['palace']['generation']}）
- 世应：{payload['analysis_hints']['shi_ying_summary']}
- 候选用神：{candidates}

| 爻位 | 输入 | 阴阳 | 动爻 | 变后 |
|---|---|---|---|---|
{line_rows}
"""


if __name__ == "__main__":
    raise SystemExit(main())
