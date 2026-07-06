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


def test_templates_include_general_real_image_and_time_layer_strategy():
    template = build_question_template("财运/交易", "问最近财运如何")

    assert "real_image_rules" in template
    assert any("先抓实象" in rule for rule in template["real_image_rules"])
    assert any(rule["layer"] == "already_formed" and "月建" in rule["evidence"] for rule in template["time_layer_rules"])
    assert any(rule["layer"] == "current_trigger" and "日辰" in rule["evidence"] for rule in template["time_layer_rules"])
    assert any(rule["layer"] == "future_development" and "动爻" in rule["evidence"] for rule in template["time_layer_rules"])
    assert any("先有利后受损" in item for item in template["already_future_split"]["reversal_patterns"])
    assert any("领域只翻译六亲象" in rule for rule in template["domain_translation_rules"])


def test_unknown_domain_returns_uncategorized_template_contract():
    template = build_question_template("综合/未分类", "随便问问")

    assert template["template_id"] == "uncategorized"
    assert template["domain"] == "综合/未分类"
    assert template["main_images"] == []
    assert template["auxiliary_images"] == []
    assert template["secondary_templates"] == []
    assert template["real_image_rules"]
    assert template["time_layer_rules"]
