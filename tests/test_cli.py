import json

from dongxuan_agent.cli import main


def test_cli_outputs_markdown(capsys):
    assert main(["2026-05-26 00:09:14", "--timezone", "Asia/Shanghai"]) == 0

    output = capsys.readouterr().out

    assert "## 大六壬课盘" in output
    assert "| 传 | 神 | 遁干 | 旺衰 | 天将 | 天官 | 六亲 |" in output
    assert "| 初传 | 子 | 庚 |" in output
    assert "青龙 | 子孙 |" in output


def test_cli_outputs_json(capsys):
    assert main(["2026-05-26 00:09:14", "--timezone", "Asia/Shanghai", "--format", "json"]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["calendar"]["day_gz"] == "庚子"
    assert payload["transmissions"]["items"] == ["子", "申", "辰"]
    assert payload["transmission_details"][0]["officer"] == "青龙"


def test_cli_outputs_number_divination_json(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--timezone",
        "Asia/Shanghai",
        "--format",
        "json",
        "--mode",
        "number",
        "--number",
        "20",
        "--gender",
        "男",
        "--question",
        "测试",
        "--birth-year",
        "1970",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["divination"]["mode"] == "number"
    assert payload["divination"]["source_hour_branch"] == "未"
    assert payload["calendar"]["hour_branch"] == "未"
    assert payload["querent"]["life_branch"] == "戌"
    assert payload["querent"]["traveling_year"] == "戌"


def test_cli_outputs_live_hour_markdown(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--mode",
        "live-hour",
        "--hour-branch",
        "子",
        "--gender",
        "女",
        "--question",
        "测试活时",
    ]) == 0

    output = capsys.readouterr().out

    assert "## 大六壬测算输入" in output
    assert "起课方式：live-hour" in output
    assert "取用时辰：子" in output
    assert "所问事：测试活时" in output
