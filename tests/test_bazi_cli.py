import json

from dongxuan_agent.bazi_cli import main


def test_bazi_cli_outputs_json(capsys):
    assert main([
        "2026-05-26 10:14:15",
        "--gender",
        "男",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["day_master"] == "庚"
    assert payload["calendar"]["hour_gz"] == "辛巳"
    assert payload["pillars"][0]["name"] == "年柱"
