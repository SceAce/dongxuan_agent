from dongxuan_agent.bazi import build_bazi_chart
from dongxuan_agent.bazi.spirits import build_bazi_spirit_sha_analysis
from dongxuan_agent.bazi_analysis import build_year_analysis_hints


def _payload():
    chart = build_bazi_chart("2006-12-18 12:30:00", timezone="Asia/Shanghai", gender="男")
    payload = chart.to_dict()
    payload["analysis_hints"] = build_year_analysis_hints(chart, 2025)
    return payload


def test_bazi_spirit_sha_analysis_has_structured_active_hits():
    result = build_bazi_spirit_sha_analysis(_payload())

    assert result["scoring_policy"].startswith("神煞为辅助加权")
    assert result["active"]
    assert result["uncertainty"]
    for item in result["active"]:
        assert set(item) >= {
            "name",
            "value",
            "value_type",
            "basis",
            "hit_positions",
            "strength",
            "supports",
            "avoid",
            "evidence",
        }
        assert item["strength"] in {"strong", "medium", "weak"}
        assert item["supports"]
        assert item["avoid"]
        assert item["evidence"]


def test_bazi_spirit_sha_hits_current_luck_and_flow_year_positions():
    result = build_bazi_spirit_sha_analysis(_payload())
    locations = {
        location
        for item in result["active"]
        for location in item["hit_positions"]
    }

    assert "当前大运支" in locations or "当前大运干" in locations
    assert "目标流年支" in locations or "目标流年干" in locations


def test_bazi_spirit_sha_omits_non_hits_from_active_scoring():
    result = build_bazi_spirit_sha_analysis(_payload())

    assert result["active"]
    assert all(item["hit_positions"] for item in result["active"])
    assert all(item["score_delta"] <= 0.2 for item in result["active"])


def test_bazi_spirit_sha_malformed_analysis_hints_soft_fails():
    payload = _payload()
    payload["analysis_hints"] = "bad"

    result = build_bazi_spirit_sha_analysis(payload)

    assert result["active"] == []
    assert result["uncertainty"]
