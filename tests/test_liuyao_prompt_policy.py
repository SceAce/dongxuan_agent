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
