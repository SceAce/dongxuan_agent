from pathlib import Path


PROMPT = Path(__file__).resolve().parents[1] / "daliuren_prompt.md"


def test_prompt_defines_issue_specific_spirit_selection():
    text = PROMPT.read_text(encoding="utf-8")

    assert "## 分测事专用神煞" in text
    assert "年运/流年" in text
    assert "感情/婚恋" in text
    assert "疾病健康" in text
    assert "失物/寻人" in text
    assert "专用神煞不等于自动取用" in text
    assert "未由工具输出" in text


def test_prompt_templates_require_structure_and_avoid_spirit_piling():
    text = PROMPT.read_text(encoding="utf-8")

    assert "每个问题模板必须按以下顺序使用" in text
    assert "先定类神" in text
    assert "再筛神煞" in text
    assert "最多 2-4 个" in text
    assert "禁止把专用神煞清单逐项解释" in text


def test_prompt_keeps_sixty_four_lesson_bodies_as_not_implemented():
    text = PROMPT.read_text(encoding="utf-8")

    assert "## 64课体使用边界" in text
    assert "lesson_bodies" in text
    assert "未由工具输出的 64 课体" in text
    assert "待校验辅助" in text
