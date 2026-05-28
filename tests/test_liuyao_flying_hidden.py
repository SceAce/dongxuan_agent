from dongxuan_agent.liuyao import build_liuyao_chart


def test_hidden_spirit_is_analyzed_through_existing_role_chain():
    payload = build_liuyao_chart(
        hexagram="否之观",
        question="问孩子考试是否顺利",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["flying_hidden_analysis"]

    assert analysis["enabled"] is True
    assert analysis["hidden_lines"]
    hidden = analysis["hidden_lines"][0]
    assert hidden["hidden_six_relative"] == "子孙"
    assert hidden["position"] == 1
    assert hidden["hidden_role_impact"] == "supports_enemy_spirit"
    assert hidden["flying_controls_hidden"] is True
    assert any(item["type"] == "hidden_enemy_spirit_supported" for item in payload["completion_chain"]["blocking_factors"])
    assert not any("飞伏未实现" in item for item in payload["completion_chain"]["unresolved"])
