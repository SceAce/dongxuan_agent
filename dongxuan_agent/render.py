from __future__ import annotations

from .chart import DaliurenChart
from .divination import DaliurenDivination


def chart_to_json(chart: DaliurenChart) -> dict:
    return chart.to_dict()


def divination_to_json(divination: DaliurenDivination) -> dict:
    return divination.to_dict()


def render_chart_markdown(chart: DaliurenChart) -> str:
    cal = chart.calendar
    plate_rows = "\n".join(
        f"| {earth} | {heaven} | {chart.heavenly_generals.get(earth, '')} | {chart.heavenly_officers.get(earth, {}).get('name', '')} | {chart.six_relatives.get(earth, {}).get('relative', '')} |"
        for earth, heaven in chart.heaven_plate.items()
    )
    lesson_rows = "\n".join(
        f"| {lesson.name} | {lesson.lower} | {lesson.upper} | {lesson.relation} |"
        for lesson in chart.four_lessons
    )
    trans_names = ["初传", "中传", "末传"]
    trans_rows = "\n".join(
        f"| {name} | {detail['branch'] or '未定'} | {detail['dun_gan'] or ''} | {detail['season_state'] or ''} | {detail['general'] or ''} | {detail['officer'] or ''} | {detail['relative'] or ''} |"
        for name, detail in zip(trans_names, chart.transmission_details, strict=True)
    )
    spirit_rows = "\n".join(
        f"| {item['name']} | {item['branch']} | {item['location']} | {item['meaning']} |"
        for item in chart.spirit_sha.get("active", [])
    ) or "| 无 | 无 | 无 | 无 |"
    uncertainty = "\n".join(f"- {item}" for item in chart.uncertainty)
    return f"""## 大六壬课盘

### 基本信息

- 时间：{cal.dt.isoformat()}
- 时区：{cal.timezone}
- 四柱：{cal.year_gz}年 {cal.month_gz}月 {cal.day_gz}日 {cal.hour_gz}时
- 月将：{chart.month_general}
- 旬空：{chart.xunkong[0]}、{chart.xunkong[1]}
- 贵人：昼贵 {chart.nobleman['day_noble']}，夜贵 {chart.nobleman['night_noble']}，本课取 {chart.nobleman['used']}（{chart.nobleman['mode']}）

### 天地盘

| 地盘 | 天盘 | 天将 | 天官 | 六亲 |
|---|---|---|---|---|
{plate_rows}

### 四课

| 课 | 下 | 上 | 关系 |
|---|---|---|---|
{lesson_rows}

### 三传

| 传 | 神 | 遁干 | 旺衰 | 天将 | 天官 | 六亲 |
|---|---|---|---|---|---|---|
{trans_rows}

- 状态：{chart.transmissions.status}
- 取法：{chart.transmissions.method}
- 说明：{chart.transmissions.note}
- 旬首：{chart.xun_dun['xun_start']}

### 简析

{chart.brief_analysis}

### 天将

{", ".join(f"{branch}:{general}" for branch, general in chart.heavenly_generals.items())}

### 天官

{", ".join(f"{branch}:{item['name']}" for branch, item in chart.heavenly_officers.items())}

### 六亲

{", ".join(f"{branch}上{item['heaven']}:{item['relative']}" for branch, item in chart.six_relatives.items())}

### 神煞

| 神煞 | 地支 | 命中位置 | 意义 |
|---|---|---|---|
{spirit_rows}

### 不确定项

{uncertainty}
"""


def render_divination_markdown(divination: DaliurenDivination) -> str:
    chart = divination.chart
    querent = divination.querent
    meta = divination.divination
    birth = querent.get("birth_year")
    birth_line = "未提供" if birth is None else f"{birth}年（{querent['birth_year_ganzhi']}，命{querent['life_branch']}）"
    traveling = querent.get("traveling_year") or "未提供"
    return f"""## 大六壬测算输入

- 起课方式：{meta['mode']}（{meta['rule']}）
- 取用时辰：{meta['source_hour_branch']}
- 性别：{querent['gender']}
- 所问事：{querent['question']}
- 当前背景：{querent.get('background') or '未提供'}
- 本命：{birth_line}
- 行年：{traveling}

{render_chart_markdown(chart)}
"""
