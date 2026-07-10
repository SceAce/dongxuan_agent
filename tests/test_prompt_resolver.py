from dongxuan_agent.apps.prompts import prompt_label, read_prompt


def test_prompt_labels_are_package_relative():
    assert prompt_label("bazi") == "dongxuan_agent/resources/prompts/bazi.md"
    assert prompt_label("daliuren") == "dongxuan_agent/resources/prompts/daliuren.md"
    assert prompt_label("liuyao") == "dongxuan_agent/resources/prompts/liuyao.md"


def test_read_prompt_returns_text():
    assert "# 八字年份事件分析 Prompt" in read_prompt("bazi")
    assert "# 大六壬测算 Prompt" in read_prompt("daliuren")
    assert "# 六爻分析 Prompt" in read_prompt("liuyao")
