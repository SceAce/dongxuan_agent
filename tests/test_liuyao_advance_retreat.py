from dongxuan_agent.liuyao import build_liuyao_chart


def test_moving_useful_god_advance_increases_support():
    payload = build_liuyao_chart(
        hexagram="晋之大有",
        question="问工作能否推进",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["advance_retreat_analysis"]

    assert analysis["enabled"] is True
    item = next(line for line in analysis["by_moving_line"] if line["position"] == 2)
    assert item["from_branch"] == "巳"
    assert item["to_branch"] == "午"
    assert item["change_type"] == "advance"
    assert item["spirit_role"] == "useful_god"
    assert item["role_impact"] == "support_increases"
    assert any(
        factor["type"] == "advance_retreat_support_increases" and factor["line"] == 2
        for factor in payload["completion_chain"]["supporting_factors"]
    )
