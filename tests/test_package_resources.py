from dongxuan_agent.apps.prompts import read_prompt


def test_all_packaged_prompts_are_readable_outside_project_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    assert "# 八字年份事件分析 Prompt" in read_prompt("bazi")
    assert "# 大六壬测算 Prompt" in read_prompt("daliuren")


def test_prompt_text_has_no_machine_specific_tool_path():
    for name in ("bazi", "daliuren"):
        assert "/home/source" not in read_prompt(name)
