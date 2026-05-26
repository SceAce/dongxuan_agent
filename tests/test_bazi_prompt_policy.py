from pathlib import Path


PROMPT = Path(__file__).resolve().parents[1] / "bazi_prompt.md"


def test_bazi_prompt_requires_analysis_hints_and_rule_cards():
    text = PROMPT.read_text(encoding="utf-8")

    assert "# 八字年份事件分析 Prompt" in text
    assert "没有八字盘，不做断语" in text
    assert "strength_analysis" in text
    assert "climate_analysis" in text
    assert "pattern_analysis" in text
    assert "不得把 V1 候选格局直接说成最终用神" in text
    assert "integrated_analysis" in text
    assert "原局定体、大运定势、流年定触发" in text
    assert "禁止只按五行数量断强弱" in text
    assert "analysis_hints" in text
    assert "rule_cards" in text
    assert "主象" in text
    assert "次象" in text
    assert "待核验点" in text


def test_bazi_prompt_forbids_candidate_piling():
    text = PROMPT.read_text(encoding="utf-8")

    assert "禁止候选清单式断法" in text
    assert "最多一个次象" in text
    assert "必须回指" in text
