from dongxuan_agent.liuyao.relations import branch_relation, element_relation, return_relation_label
from dongxuan_agent.liuyao.strength import effective_strength, extreme_state, seasonal_state


def test_si_month_maps_elements_to_wang_xiang_xiu_qiu_si():
    assert seasonal_state("火", "巳") == "旺"
    assert seasonal_state("土", "巳") == "相"
    assert seasonal_state("木", "巳") == "休"
    assert seasonal_state("水", "巳") == "囚"
    assert seasonal_state("金", "巳") == "死"


def test_branch_relation_supports_same_clash_and_combine_only():
    assert branch_relation("巳", "巳") == "same"
    assert branch_relation("巳", "亥") == "clash"
    assert branch_relation("寅", "亥") == "combine"
    assert branch_relation("巳", "酉") == "none"


def test_element_relation_is_directional():
    assert element_relation("木", "火") == "generates"
    assert element_relation("火", "木") == "generated_by"
    assert element_relation("水", "火") == "controls"
    assert element_relation("火", "水") == "controlled_by"
    assert element_relation("土", "土") == "same"


def test_return_relation_labels_changed_line_direction():
    assert return_relation_label("木", "水") == "回头生"
    assert return_relation_label("木", "金") == "回头克"
    assert return_relation_label("火", "火") == "比和"
    assert return_relation_label("火", "土") == "泄气"
    assert return_relation_label("金", "木") == "耗气"


def test_extreme_state_requires_multiple_clear_factors():
    assert extreme_state(
        "旺",
        support_factors=["日辰生扶", "动爻发动"],
        weakening_factors=[],
    ) == "over_strong"
    assert extreme_state(
        "死",
        support_factors=[],
        weakening_factors=["日辰克制", "旬空"],
    ) == "over_weak"
    assert extreme_state(
        "旺",
        support_factors=["日辰生扶"],
        weakening_factors=["旬空"],
    ) == "none"


def test_effective_strength_returns_coarse_labels():
    assert effective_strength("旺", ["日辰生扶"], []) == "strong"
    assert effective_strength("死", [], ["旬空"]) == "very_weak"
    assert effective_strength("休", [], []) == "balanced"
