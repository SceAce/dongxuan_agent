from dongxuan_agent.liuyao import build_liuyao_chart


def test_li_dayou_detects_si_you_chou_full_combination_supporting_original_spirit():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作 offer 合同什么时候下来",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["combination_analysis"]
    assert analysis["enabled"] is True
    group = next(item for item in analysis["groups"] if item["element"] == "金" and set(item["branches"]) >= {"巳", "酉"})

    assert group["type"] == "full_three_combination"
    assert group["role_impact"] == "supports_original_spirit"
    assert set(group["line_positions"]) >= {2, 4, 6}
