import pytest

from dongxuan_agent.bazi.discipline import build_discipline_profile, build_middle_image_scores


def test_middle_image_scores_accepts_score_shaped_base_and_preserves_evidence():
    result = build_middle_image_scores(
        {"信息处理": {"score": 1.2, "evidence": ["结构证据"]}},
        {},
    )

    assert result["信息处理"]["base_score"] == 1.2
    assert result["信息处理"]["final_score"] == 1.2
    assert result["信息处理"]["evidence"] == ["结构证据"]


def test_middle_image_scores_caps_individual_spirit_hit():
    result = build_middle_image_scores(
        {"信息处理": {"base_score": 1.0}},
        {
            "active": [
                {
                    "name": "文昌",
                    "supports": ["信息处理"],
                    "score_delta": 0.6,
                    "hit_positions": ["年柱"],
                    "strength": "强",
                    "basis": "命中",
                    "avoid": "不直接定专业",
                }
            ]
        },
    )

    assert result["信息处理"]["spirit_delta"] <= 0.2


def test_middle_image_scores_caps_total_spirit_delta_per_image():
    result = build_middle_image_scores(
        {"信息处理": {"base_score": 1.0}},
        {
            "active": [
                {"name": "文昌", "supports": ["信息处理"], "score_delta": 0.2},
                {"name": "学堂", "supports": ["信息处理"], "score_delta": 0.2},
                {"name": "词馆", "supports": ["信息处理"], "score_delta": 0.2},
            ]
        },
    )

    assert result["信息处理"]["spirit_delta"] <= 0.35


def test_middle_image_scores_caps_single_spirit_hit_without_structural_base():
    result = build_middle_image_scores(
        {},
        {"active": [{"name": "文昌", "supports": ["信息处理"], "score_delta": 0.2}]},
    )

    assert result["信息处理"]["base_score"] == 0
    assert result["信息处理"]["spirit_delta"] <= 0.08


def test_middle_image_scores_spirit_evidence_keeps_prompt_safety_context():
    result = build_middle_image_scores(
        {"信息处理": {"base_score": 1.0}},
        {
            "active": [
                {
                    "name": "文昌",
                    "supports": ["信息处理"],
                    "score_delta": 0.12,
                    "hit_positions": ["年柱", "时柱"],
                    "strength": "中",
                    "basis": "日主见文昌",
                    "avoid": "不直接定专业",
                }
            ]
        },
    )

    evidence = " ".join(result["信息处理"]["evidence"])
    assert "文昌" in evidence
    assert "中" in evidence
    assert "日主见文昌" in evidence
    assert "年柱、时柱" in evidence
    assert "0.12" in evidence
    assert "不直接" in evidence


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


@pytest.mark.parametrize("middle_scores", [{}, {"未知画像": {"final_score": 2.0}}])
def test_discipline_profile_filters_empty_unsupported_groups(middle_scores):
    result = build_discipline_profile(middle_scores)

    assert result["groups"] == []
    assert result["cross_domain"] is False
    assert result["recommended_mode"].startswith("证据不足")
