from dongxuan_agent.chart import build_chart
from dongxuan_agent.divination import build_divination
from dongxuan_agent.render import (
    chart_to_json,
    divination_to_json,
    render_chart_markdown,
    render_divination_markdown,
)


def test_render_chart_markdown_contains_required_sections():
    chart = build_chart("2026-05-25 12:30", timezone="Asia/Shanghai")

    rendered = render_chart_markdown(chart)

    assert "## 大六壬课盘" in rendered
    assert "四柱" in rendered
    assert "月将" in rendered
    assert "天地盘" in rendered
    assert "四课" in rendered
    assert "三传" in rendered
    assert "天将" in rendered
    assert "天官" in rendered
    assert "六亲" in rendered
    assert "神煞" in rendered
    assert "贵人" in rendered
    assert "| 传 | 神 | 遁干 | 旺衰 | 天将 | 天官 | 六亲 |" in rendered
    assert "不确定项" in rendered


def test_chart_to_json_preserves_machine_fields():
    chart = build_chart("2026-05-25 12:30", timezone="Asia/Shanghai")

    payload = chart_to_json(chart)

    assert payload["calendar"]["hour_gz"] == chart.calendar.hour_gz
    assert payload["heaven_plate"] == chart.heaven_plate
    assert payload["transmissions"]["status"] == chart.transmissions.status
    assert payload["heavenly_officers"] == chart.heavenly_officers
    assert payload["six_relatives"] == chart.six_relatives
    assert payload["spirit_sha"] == chart.spirit_sha
    assert payload["transmission_details"] == chart.transmission_details
    assert payload["xun_dun"] == chart.xun_dun
    assert payload["lesson_bodies"] == chart.lesson_bodies
    assert payload["brief_analysis"] == chart.brief_analysis


def test_render_chart_markdown_contains_xun_dun_and_season_state():
    chart = build_chart("2026-05-26 11:58:00", timezone="Asia/Shanghai")

    rendered = render_chart_markdown(chart)

    assert "| 传 | 神 | 遁干 | 旺衰 | 天将 | 天官 | 六亲 |" in rendered
    assert "| 初传 | 辰 |  | 相 | 合 | 六合 | 父母 |" in rendered
    assert "| 中传 | 午 | 甲 | 旺 | 龙 | 青龙 | 官鬼 |" in rendered
    assert "旬首：甲午" in rendered


def test_divination_render_and_json_include_querent_fields():
    divination = build_divination(
        "2026-05-26 10:14:15",
        mode="number",
        number=20,
        gender="男",
        question="测试报数",
        birth_year=1970,
    )

    payload = divination_to_json(divination)
    rendered = render_divination_markdown(divination)

    assert payload["divination"]["source_hour_branch"] == "未"
    assert payload["querent"]["birth_year_ganzhi"] == "庚戌"
    assert "## 大六壬测算输入" in rendered
    assert "本命：1970年（庚戌，命戌）" in rendered
    assert "行年：戌" in rendered
