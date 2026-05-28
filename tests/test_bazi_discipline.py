from dongxuan_agent.bazi.discipline import build_discipline_profile


def test_discipline_profile_scores_cross_domain_when_groups_are_close():
    middle_scores = {
        "信息处理": {"final_score": 1.5, "evidence": ["信息处理成立"]},
        "公共传播": {"final_score": 1.4, "evidence": ["公共传播成立"]},
        "文本表达": {"final_score": 1.2, "evidence": ["文本表达成立"]},
    }
    result = build_discipline_profile(middle_scores, question="适合什么专业")

    assert result["cross_domain"] is True
    assert result["groups"][0]["name"] in {"information_data", "media_communication"}
    assert "不得强行归为纯文或纯理" in result["constraints_for_llm"]


def test_discipline_profile_keeps_strong_engineering_dominant_with_humanities_spirit():
    middle_scores = {
        "工程系统": {"final_score": 2.0, "evidence": ["金土结构强"]},
        "技能输出": {"final_score": 1.8, "evidence": ["食伤项目输出"]},
        "文本表达": {"final_score": 0.9, "evidence": ["文昌辅助，但结构弱"]},
    }
    result = build_discipline_profile(middle_scores, question="高考后学什么专业")

    assert result["groups"][0]["name"] == "stem_engineering"
    assert result["groups"][0]["score"] > 2.5
    assert result["cross_domain"] is False


def test_discipline_profile_has_structured_group_evidence():
    middle_scores = {
        "制度法理": {"final_score": 1.4, "evidence": ["官印规则成立"]},
        "信息处理": {"final_score": 1.3, "evidence": ["信息处理成立"]},
    }
    result = build_discipline_profile(middle_scores, question="职业方向")

    for group in result["groups"]:
        assert set(group) >= {
            "name",
            "score",
            "supporting_images",
            "spirit_factors",
            "structural_evidence",
            "weakening_factors",
            "confidence",
        }
