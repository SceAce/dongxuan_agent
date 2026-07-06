import json

from dongxuan_agent.liuyao_cli import main as chart_main


def test_liuyao_cli_outputs_json_for_manual_lines(capsys):
    assert chart_main([
        "--lines",
        "少阳 老阴 少阴 少阳 老阳 少阴",
        "--question",
        "问工作",
        "--datetime",
        "2026-05-28 09:30:00",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["schema"] == "liuyao_chart_v11"
    assert payload["input"]["method"] == "manual_lines"
    assert payload["hexagram"]["moving_lines"] == [2, 5]
    assert payload["derived_lines"]
    assert payload["relations"]["moving_effects"]
    assert payload["useful_god_selection"]["principle"] == "近取诸身，远取诸象"
    assert payload["question_template"]["template_id"] == "career_work"
    assert payload["six_spirits"]["scope"] == "辅助取象，不作主裁决"
    assert payload["advanced_layers"]["enabled"] == ["spirit_roles", "twelve_stages", "three_combination", "flying_hidden", "advance_retreat", "timing", "spirit_sha"]
    assert payload["completion_chain"]["mode"] == "spirit_role_completion"
    assert payload["twelve_stage_analysis"]["enabled"] is True
    assert payload["combination_analysis"]["enabled"] is True
    assert payload["flying_hidden_analysis"]["enabled"] is True
    assert payload["advance_retreat_analysis"]["enabled"] is True
    assert payload["timing_analysis"]["enabled"] is True
    assert payload["spirit_sha_analysis"]["enabled"] is True


def test_liuyao_cli_outputs_json_for_named_hexagram(capsys):
    assert chart_main([
        "--hexagram",
        "离之大有",
        "--question",
        "问合同",
        "--datetime",
        "2026-05-28 09:30:00",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["hexagram"]["original"]["name"] == "离为火"
    assert payload["hexagram"]["changed"]["name"] == "火天大有"


def test_liuyao_cli_outputs_json_for_random_lines(capsys):
    assert chart_main([
        "--random",
        "--seed",
        "7",
        "--question",
        "问财运",
        "--datetime",
        "2026-05-28 09:30:00",
        "--format",
        "json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)

    assert payload["input"]["method"] == "random_lines"
    assert len(payload["lines"]) == 6
    assert payload["prompt_contract"]["output_sections"]
