from __future__ import annotations

import json
import unicodedata

from dongxuan_agent.core.constants import BRANCH_YINYANG, STEM_YINYANG

from .chart import DaliurenChart
from .divination import DaliurenDivination


def chart_to_json(chart: DaliurenChart) -> dict:
    return chart.to_dict()


def divination_to_json(divination: DaliurenDivination) -> dict:
    return divination.to_dict()


_PLATE_LAYOUT: tuple[tuple[str | None, ...], ...] = (
    ("巳", "午", "未", "申"),
    ("辰", None, None, "酉"),
    ("卯", None, None, "戌"),
    ("寅", "丑", "子", "亥"),
)


def _display_width(value: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in "WFA" else 1 for char in value)


def _pad_center(value: str, width: int) -> str:
    missing = max(width - _display_width(value), 0)
    left = missing // 2
    return " " * left + value + " " * (missing - left)


def _short_relative(relative: str | None) -> str:
    return {
        "父母": "父",
        "兄弟": "兄",
        "子孙": "子",
        "妻财": "财",
        "官鬼": "官",
    }.get(relative or "", "")


def _yinyang(value: str) -> str:
    return STEM_YINYANG.get(value) or BRANCH_YINYANG.get(value, "")


def _render_plate_traditional(chart: DaliurenChart) -> str:
    """Render the fixed twelve-palace layout without losing machine fields."""
    cell_width = 16

    def cell(earth: str | None, compact: bool = False) -> str:
        if earth is None:
            return " " * cell_width
        general = chart.heavenly_generals.get(earth, "")
        officer = chart.heavenly_officers.get(earth, {}).get("name", "")
        heaven = chart.heaven_plate.get(earth, "")
        if compact:
            value = f"{general}({officer}) {heaven}/{earth}"
        else:
            value = f"{general}({officer})"
        return _pad_center(value, cell_width)

    # The top and bottom rows follow the traditional two-line presentation;
    # side palaces keep the general and branch pair on one line.
    lines = [
        "（天将〔天官〕；格内为天盘/地盘）",
        "        " + "".join(cell(earth) for earth in _PLATE_LAYOUT[0]),
        "        " + "".join(_pad_center(f"{chart.heaven_plate.get(earth, '')}/{earth}", cell_width) for earth in _PLATE_LAYOUT[0]),
        "".join(cell(earth, compact=True) for earth in _PLATE_LAYOUT[1]),
        "".join(cell(earth, compact=True) for earth in _PLATE_LAYOUT[2]),
        "        " + "".join(cell(earth) for earth in _PLATE_LAYOUT[3]),
        "        " + "".join(_pad_center(f"{chart.heaven_plate.get(earth, '')}/{earth}", cell_width) for earth in _PLATE_LAYOUT[3]),
    ]
    return "\n".join(lines)


def _render_lessons_traditional(chart: DaliurenChart) -> str:
    lessons = tuple(reversed(chart.four_lessons))
    labels = tuple(lesson.name for lesson in lessons)
    width = 12

    def row(label: str, values: list[str]) -> str:
        return _pad_center(label, 8) + "".join(_pad_center(value, width) for value in values)

    officers = [
        chart.heavenly_officers.get(lesson.lower_branch, {}).get("name", "")
        for lesson in lessons
    ]
    upper = [lesson.upper for lesson in lessons]
    lower = [lesson.lower_branch for lesson in lessons]
    gan_zhi = [lesson.lower for lesson in lessons]
    yinyang = [_yinyang(lesson.lower) for lesson in lessons]
    relations = [lesson.relation for lesson in lessons]
    return "\n".join(
        [
            "（横列从右至左为一课、二课、三课、四课）",
            row("课名", list(labels)),
            row("天官", officers),
            row("上神", upper),
            row("下神", lower),
            row("干支", gan_zhi),
            row("阴阳", yinyang),
            row("关系", relations),
        ]
    )


def _render_transmissions_traditional(chart: DaliurenChart) -> str:
    width = 8

    def row(label: str, values: list[str]) -> str:
        return _pad_center(label, width) + "".join(_pad_center(value, width) for value in values)

    transmission_labels = ["初", "中", "末"]
    rows = []
    for label, detail in zip(transmission_labels, chart.transmission_details, strict=True):
        earth = detail.get("earth") or ""
        officer = chart.heavenly_officers.get(earth, {}).get("short", "") if earth else ""
        rows.append(
            row(
                label,
                [
                    _short_relative(detail.get("relative")),
                    detail.get("dun_gan") or "",
                    detail.get("branch") or "",
                    officer,
                ],
            )
        )
    return "\n".join(
        [
            "（六亲、遁干、三传、天官均取简称；旬空遁干留空）",
            row("传", ["六亲", "遁干", "支", "天官"]),
            *rows,
        ]
    )


def render_chart_markdown(chart: DaliurenChart) -> str:
    cal = chart.calendar
    plate_preview = json.dumps(chart.to_dict()["plate_preview"], ensure_ascii=False, indent=2)
    plate_rows = "\n".join(
        f"| {earth} | {heaven} | {chart.heavenly_generals.get(earth, '')} | {chart.heavenly_officers.get(earth, {}).get('name', '')} | {chart.six_relatives.get(earth, {}).get('relative', '')} |"
        for earth, heaven in chart.heaven_plate.items()
    )
    lesson_rows = "\n".join(
        f"| {lesson.name} | {lesson.lower} | {lesson.lower_branch} | {lesson.upper} | {lesson.relation} | {chart.heavenly_generals.get(lesson.lower_branch, '')} | {chart.heavenly_officers.get(lesson.lower_branch, {}).get('name', '')} | {chart.six_relatives.get(lesson.lower_branch, {}).get('relative', '')} |"
        for lesson in reversed(chart.four_lessons)
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

### 盘面结构

```json
{plate_preview}
```

### 基本信息

- 时间：{cal.dt.isoformat()}
- 时区：{cal.timezone}
- 四柱：{cal.year_gz}年 {cal.month_gz}月 {cal.day_gz}日 {cal.hour_gz}时
- 月将：{chart.month_general}
- 旬空：{chart.xunkong[0]}、{chart.xunkong[1]}
- 贵人：昼贵 {chart.nobleman['day_noble']}，夜贵 {chart.nobleman['night_noble']}，本课取 {chart.nobleman['used']}（{chart.nobleman['mode']}）

### 天地盘

```text
{_render_plate_traditional(chart)}
```

| 地盘 | 天盘 | 天将 | 天官 | 六亲 |
|---|---|---|---|---|
{plate_rows}

### 四课

```text
{_render_lessons_traditional(chart)}
```

| 课 | 下 | 下地盘 | 上 | 关系 | 天将 | 天官 | 六亲 |
|---|---|---|---|---|---|---|---|
{lesson_rows}

### 三传

```text
{_render_transmissions_traditional(chart)}
```

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
