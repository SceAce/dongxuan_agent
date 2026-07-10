import json

import pytest

from dongxuan_agent.bazi.cli import main


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


def test_bazi_cli_does_not_expose_legacy_zi_hour_selector(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "--zi-hour-rule" not in capsys.readouterr().out
