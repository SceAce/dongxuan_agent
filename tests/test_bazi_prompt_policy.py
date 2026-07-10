from dongxuan_agent.apps.prompts import read_prompt


PROMPT = read_prompt("bazi")


def test_bazi_prompt_requires_analysis_hints_and_rule_cards():
    text = PROMPT

    assert "# 八字年份事件分析 Prompt" in text
    assert "没有八字盘，不做断语" in text
    assert "strength_analysis" in text
    assert "climate_analysis" in text
    assert "pattern_analysis" in text
    assert "不得把 V1 候选格局直接说成最终用神" in text
    assert "remedy_analysis" in text
    assert "god_candidates" in text
    assert "luck_year_remedy" in text
    assert "禁止把候选用神当最终用神" in text
    assert "imagery_analysis" in text
    assert "没有 evidence 的象不得输出" in text
    assert "integrated_analysis" in text
    assert "原局定体、大运定势、流年定触发" in text
    assert "禁止只按五行数量断强弱" in text
    assert "analysis_hints" in text
    assert "rule_cards" in text
    assert "knowledge_layers" in text
    assert "理法 -> 象法 -> 案例" in text
    assert "主象" in text
    assert "次象" in text
    assert "待核验点" in text


def test_bazi_prompt_forbids_candidate_piling():
    text = PROMPT

    assert "禁止候选清单式断法" in text
    assert "最多一个次象" in text
    assert "必须回指" in text
    assert "主断优先" in text
    assert "多方验证" in text


def test_bazi_prompt_constrains_major_and_career_identification():
    text = PROMPT

    assert "专业/职业/行业识别题" in text
    assert "抽象取象画像" in text
    assert "知识库象义" in text
    assert "最多两个现实落点" in text
    assert "每个现实落点只能是一个原子专业、行业或职业方向" in text
    assert "不得在同一个落点里用顿号、斜杠或逗号堆叠多个方向" in text
    assert "禁止把五行、十神、干支直接等同于现实专业、行业或职业" in text
    assert "必须先读取 `strength_analysis.element_forces.*.season_power`" in text
    assert "不得按五行或十神出现即展开类象" in text
    assert "symbolic_dynamics" in text
    assert "direction_profile" in text
    assert "knowledge_query_terms" in text
    assert "knowledge_sources" in text
    assert (
        "如有 `imagery_analysis.answer_guidance.major_or_career_identification.discipline_profile`"
        in text
    )
    assert "若无该字段，不得编造专业族群画像" in text


def test_bazi_prompt_constrains_model_assisted_major_landing():
    text = PROMPT

    assert "discipline_profile" in text
    assert "神煞只作辅助加权" in text
    assert "不得强行归为纯文或纯理" in text
    assert "联网检索只能用于解释现代专业实际学习内容" in text
    assert "不得覆盖命盘画像裁决" in text
    assert "若有 `discipline_profile`" in text
    assert "若有 `spirit_sha_analysis.active`" in text
    assert "案例层" in text
    assert "禄命派" in text
