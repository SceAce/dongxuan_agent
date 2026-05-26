from __future__ import annotations

import argparse
import json
from datetime import datetime

from .bazi import BaziChart, build_bazi_chart


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="排八字四柱并输出 Markdown 或 JSON。")
    parser.add_argument("datetime", nargs="?", help="出生时间，例如 '2026-05-26 10:14:15'；缺省为当前时间。")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="时区，默认 Asia/Shanghai。")
    parser.add_argument("--gender", choices=("男", "女"), help="性别，可选。")
    parser.add_argument("--longitude", type=float, help="出生地经度；提供后按经度近似校正真太阳时。")
    parser.add_argument("--zi-hour-rule", choices=("whole", "split"), default="whole", help="子时规则：whole 不拆分；split 晚子换日。")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="输出格式。")
    args = parser.parse_args(argv)

    value = args.datetime or datetime.now().isoformat(timespec="seconds")
    chart = build_bazi_chart(
        value,
        timezone=args.timezone,
        gender=args.gender,
        longitude=args.longitude,
        zi_hour_rule=args.zi_hour_rule,
    )
    if args.format == "json":
        print(json.dumps(chart.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_bazi_markdown(chart))
    return 0


def render_bazi_markdown(chart: BaziChart) -> str:
    payload = chart.to_dict()
    rows = "\n".join(
        f"| {pillar['name']} | {pillar['ganzhi']} | {pillar['stem_ten_god']} | "
        f"{'、'.join(item['stem'] + ':' + item['ten_god'] for item in pillar['hidden_stems'])} |"
        for pillar in payload["pillars"]
    )
    relationships = "、".join(
        f"{item['branches']}{item['type']}" for item in payload["branch_relationships"]
    ) or "无"
    return f"""## 八字排盘

- 时间：{payload['calendar']['datetime']}
- 时区：{payload['calendar']['timezone']}
- 性别：{payload['gender'] or '未提供'}
- 四柱：{payload['calendar']['year_gz']}年 {payload['calendar']['month_gz']}月 {payload['calendar']['day_gz']}日 {payload['calendar']['hour_gz']}时
- 日主：{payload['day_master']}
- 旬空：{'、'.join(payload['xunkong'])}

| 柱 | 干支 | 天干十神 | 藏干十神 |
|---|---|---|---|
{rows}

- 地支关系：{relationships}
"""


if __name__ == "__main__":
    raise SystemExit(main())
