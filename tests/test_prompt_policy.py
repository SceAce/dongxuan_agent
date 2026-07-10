from dongxuan_agent.apps.prompts import read_prompt

PROMPT = read_prompt("daliuren")


def test_prompt_defines_issue_specific_spirit_selection():
    text = PROMPT

    assert "## 分测事专用神煞" in text
    assert "年运/流年" in text
    assert "感情/婚恋" in text
    assert "疾病健康" in text
    assert "失物/寻人" in text
    assert "专用神煞不等于自动取用" in text
    assert "未由工具输出" in text


def test_prompt_templates_require_structure_and_avoid_spirit_piling():
    text = PROMPT

    assert "每个问题模板必须按以下顺序使用" in text
    assert "先定类神" in text
    assert "再筛神煞" in text
    assert "最多 2-4 个" in text
    assert "禁止把专用神煞清单逐项解释" in text


def test_prompt_keeps_sixty_four_lesson_bodies_as_not_implemented():
    text = PROMPT

    assert "## 64课体使用边界" in text
    assert "lesson_bodies" in text
    assert "未由工具输出的 64 课体" in text
    assert "待校验辅助" in text


def test_prompt_matches_current_daliuren_casting_rules():
    text = PROMPT

    assert "性别：可选" in text
    assert "“巳”和“巳时”都取巳时" in text
    assert "0/23 为子" in text
    assert "9/10 为巳" in text
    assert "30 -> 6 -> 卯" in text
    assert "天地盘、四课、三传" in text
    assert "三传必须包含遁干、旺衰、天将、天官、六亲" in text
    assert "knowledge_layers" in text
    assert "理法 > 象根 > 案例" in text
    assert "子1、丑2至亥12" not in text
