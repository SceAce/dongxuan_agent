from pathlib import Path


PROMPT = Path("liuyao_prompt.md").read_text(encoding="utf-8")


def test_liuyao_prompt_has_minimal_loop_sections():
    for section in ["卦体摘要", "用神定位", "世应关系", "旺衰与月日", "动变作用", "综合倾向", "不确定项"]:
        assert f"## {section}" in PROMPT


def test_liuyao_prompt_requires_v2_fields_and_forbids_unsupported_rules():
    for field in ["derived_lines", "useful_god_analysis", "useful_god_selection", "relations.month_day", "relations.shi_ying", "relations.moving_effects"]:
        assert field in PROMPT
    for forbidden in ["六神", "飞伏", "三合局", "应期", "八字旺衰", "大六壬四课三传"]:
        assert forbidden in PROMPT
    assert "不得把旺直接视为吉" in PROMPT
    assert "不得把死直接视为凶" in PROMPT


def test_liuyao_prompt_preserves_layered_useful_god_conflicts():
    for text in ["近取诸身", "远取诸象", "layered", "ambiguous", "不能强行压成单一用神"]:
        assert text in PROMPT


def test_liuyao_prompt_requires_templates_and_six_spirits_as_auxiliary_only():
    for text in ["question_template", "six_spirits", "辅助取象，不作主裁决", "青龙必吉", "白虎必凶", "玄武必欺瞒", "auxiliary_marks.enabled"]:
        assert text in PROMPT
    assert "不能单凭青龙断吉" in PROMPT
    assert "不能单凭白虎断凶" in PROMPT
    assert "不得在 prompt 中编造命中" in PROMPT


def test_liuyao_prompt_requires_spirit_roles_and_advanced_layer_order():
    for text in ["spirit_role_analysis", "completion_chain", "advanced_layers", "原神", "忌神", "仇神", "闲神"]:
        assert text in PROMPT
    assert "先看用神，再看原神，再看忌神，再看仇神" in PROMPT
    assert "动爻必须先按 spirit_role 判断" in PROMPT
    assert "只有 advanced_layers.enabled 中的层可以作为证据" in PROMPT
    assert "不得输出具体应期" in PROMPT


def test_liuyao_prompt_requires_role_aware_twelve_stages():
    for text in ["twelve_stage", "twelve_stage_analysis", "十二长生", "状态辅助，不直接定吉凶"]:
        assert text in PROMPT
    assert "十二长生必须先按 spirit_role 解释" in PROMPT
    assert "twelve_stages" in PROMPT


def test_liuyao_prompt_requires_role_aware_three_combination():
    for text in ["combination_analysis", "三合", "role_impact"]:
        assert text in PROMPT
    assert "三合必须按 role_impact 解释" in PROMPT
    assert "不得单凭三合断吉凶" in PROMPT


def test_liuyao_prompt_requires_bounded_flying_hidden():
    for text in ["flying_hidden_analysis", "飞伏", "不得编造伏神", "najia.hidden_spirits"]:
        assert text in PROMPT
    assert "不得输出具体应期" in PROMPT
