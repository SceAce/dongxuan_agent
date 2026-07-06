from dongxuan_agent.liuyao import build_liuyao_chart


def test_timing_uses_advance_retreat_changed_branch_as_candidate():
    payload = build_liuyao_chart(
        hexagram="晋之大有",
        question="问工作能否推进",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["timing_analysis"]

    assert analysis["enabled"] is True
    assert analysis["scope"] == "应期只输出地支候选触发点，不输出公历日期。"
    assert any(
        item["branch"] == "午"
        and item["basis"] == "advance_retreat_value"
        and item["source"] == "advance_retreat_analysis"
        and item["line"] == 2
        for item in analysis["candidates"]
    )
    assert "当前不换算公历日期。" in analysis["unresolved"]
