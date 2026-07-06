from dongxuan_agent.liuyao.twelve_stages import twelve_stage


def test_twelve_stage_table_maps_element_and_branch():
    assert twelve_stage("水", "亥")["stage"] == "临官"
    assert twelve_stage("土", "丑")["stage"] == "衰"
    assert twelve_stage("金", "酉")["stage"] == "帝旺"
    assert twelve_stage("水", "亥")["strength_hint"] == "growth"
    assert twelve_stage("金", "酉")["strength_hint"] == "peak"
