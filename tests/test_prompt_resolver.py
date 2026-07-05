from pathlib import Path

from dongxuan_agent.apps.prompts import prompt_label, prompt_path, read_prompt


def test_prompt_path_points_to_canonical_prompt_dir():
    project_root = Path(__file__).resolve().parents[1]

    assert prompt_path("bazi") == project_root / "prompts" / "bazi.md"
    assert prompt_path("daliuren") == project_root / "prompts" / "daliuren.md"
    assert prompt_path("liuyao") == project_root / "prompts" / "liuyao.md"


def test_prompt_label_is_repo_relative():
    assert prompt_label("bazi") == "prompts/bazi.md"
    assert prompt_label("daliuren") == "prompts/daliuren.md"
    assert prompt_label("liuyao") == "prompts/liuyao.md"


def test_read_prompt_returns_text():
    assert "# 八字年份事件分析 Prompt" in read_prompt("bazi")
    assert "# 大六壬测算 Prompt" in read_prompt("daliuren")
    assert "# 六爻分析 Prompt" in read_prompt("liuyao")
