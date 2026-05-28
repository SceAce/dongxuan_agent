from dongxuan_agent.liuyao.templates import build_question_template


def test_career_work_template_selects_main_and_auxiliary_images():
    template = build_question_template("事业/工作", "问工作 offer 合同什么时候下来")

    assert template["template_id"] == "career_work"
    assert template["domain"] == "事业/工作"
    assert "question_context.domain" in template["selected_by"]
    assert any(item["six_relative"] == "官鬼" for item in template["main_images"])
    assert any(item["six_relative"] == "父母" for item in template["auxiliary_images"])
    assert any("工作 + 合同" in rule for rule in template["conflict_rules"])
    assert "模板只决定取象入口，不决定最终成败。" in template["must_not_mix"]


def test_unknown_domain_returns_uncategorized_template_contract():
    template = build_question_template("综合/未分类", "随便问问")

    assert template["template_id"] == "uncategorized"
    assert template["domain"] == "综合/未分类"
    assert template["main_images"] == []
    assert template["auxiliary_images"] == []
    assert template["secondary_templates"] == []
