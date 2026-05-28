from dongxuan_agent.liuyao import build_liuyao_chart


def test_derived_lines_merge_line_najia_useful_god_and_strength():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert payload["schema"] == "liuyao_chart_v4"
    assert payload["question_template"]["template_id"] == "career_work"
    line = payload["derived_lines"][2]
    assert line["position"] == 3
    assert line["stem_branch"] == "己亥"
    assert line["six_relative"] == "官鬼"
    assert line["role"] == "应"
    assert line["is_ying"] is True
    assert line["is_candidate_useful_god"] is True
    assert line["month_state"]["seasonal_state"] == "囚"
    assert line["month_state"]["branch_relation"] == "clash"
    assert line["day_state"]["branch_relation"] == "combine"
    assert line["void_state"]["is_void"] is False
    assert line["effective_strength"] in {"very_strong", "strong", "balanced", "weak", "very_weak"}
    assert line["extreme_state"] in {"over_strong", "over_weak", "none"}
    assert line["strength_evidence"]
    assert line["six_spirit"]["spirit"] == "朱雀"


def test_useful_god_analysis_maps_candidates_to_matching_lines():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["useful_god_analysis"]
    primary = analysis["candidates"][0]
    assert primary["six_relative"] == "官鬼"
    assert primary["priority"] == "primary"
    assert primary["matching_lines"][0]["position"] == 3
    assert "候选用神不等于最终用神" in primary["selection_constraints"]


def test_relations_include_month_day_shi_ying_and_moving_effects():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    relations = payload["relations"]
    assert relations["month_day"]["month_branch"] == "巳"
    assert relations["month_day"]["by_line"][2]["month"]["seasonal_state"] == "囚"
    assert relations["shi_ying"]["shi_position"] == 6
    assert relations["shi_ying"]["ying_position"] == 3
    assert relations["shi_ying"]["summary"]
    moving = relations["moving_effects"][0]
    assert moving["actor_position"] == 2
    assert {target["target"] for target in moving["targets"]} >= {"shi", "ying", "candidate_useful_god"}
    assert moving["changed_line"]["return_label"] in {"回头生", "回头克", "比和", "泄气", "耗气", "无直接作用"}


def test_judgment_frame_and_prompt_contract_exist():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作",
        value="2026-05-28 09:30:00",
    ).to_dict()

    assert payload["judgment_frame"]["mode"] == "minimal_loop"
    assert [step["name"] for step in payload["judgment_frame"]["steps"]] == [
        "question_domain",
        "locate_useful_gods",
        "check_shi_ying",
        "check_month_day_strength",
        "check_moving_changed_lines",
        "synthesize",
    ]
    assert "derived_lines" in payload["prompt_contract"]["must_use_fields"]
    assert "useful_god_selection" in payload["prompt_contract"]["must_use_fields"]
    assert "question_template" in payload["prompt_contract"]["must_use_fields"]
    assert "six_spirits" in payload["prompt_contract"]["must_use_fields"]
    assert "未实现的神煞命中" in payload["prompt_contract"]["must_not_infer"]
