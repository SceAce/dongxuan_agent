from dongxuan_agent.liuyao import build_liuyao_chart


def test_work_offer_derives_spirit_roles_from_main_useful_god():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作 offer 合同什么时候下来",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["spirit_role_analysis"]

    assert analysis["status"] == "ready"
    assert analysis["main_useful_god"] == "官鬼"
    assert analysis["useful_god_elements"] == ["水"]
    assert analysis["role_elements"]["original_spirit"] == ["金"]
    assert analysis["role_elements"]["avoiding_spirit"] == ["土"]
    assert analysis["role_elements"]["enemy_spirit"] == ["火"]

    roles = {line["position"]: line["role"] for line in analysis["by_line"]}
    assert roles[3] == "useful_god"
    assert roles[2] == "avoiding_spirit"
    assert roles[4] == "original_spirit"
    assert roles[6] == "enemy_spirit"


def test_completion_chain_marks_moving_avoiding_spirit_as_blocking():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作 offer 合同什么时候下来",
        value="2026-05-28 09:30:00",
    ).to_dict()

    chain = payload["completion_chain"]

    assert chain["mode"] == "spirit_role_completion"
    assert chain["tendency"] in {"blocked", "mixed"}
    assert chain["tendency"] != "supported"
    assert any(item["type"] == "useful_god_present" and item["line"] == 3 for item in chain["supporting_factors"])
    assert any(
        item["type"] == "avoiding_spirit_moving_controls_useful_god"
        and item["line"] == 2
        and item["target_line"] == 3
        for item in chain["blocking_factors"]
    )
    assert any(item["type"] == "layered_auxiliary" for item in chain["mixed_factors"])
