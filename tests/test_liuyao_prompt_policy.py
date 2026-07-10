from dongxuan_agent.apps.prompts import read_prompt


PROMPT = read_prompt("liuyao")


def test_liuyao_prompt_has_minimal_loop_sections():
    prompt = PROMPT

    for section in ["卦体摘要", "用神定位", "世应关系", "旺衰与月日", "动变作用", "综合倾向", "不确定项"]:
        assert f"## {section}" in prompt


def test_liuyao_prompt_requires_v2_fields_and_forbids_unsupported_rules():
    prompt = PROMPT

    for field in ["derived_lines", "useful_god_analysis", "useful_god_selection", "relations.month_day", "relations.shi_ying", "relations.moving_effects"]:
        assert field in prompt
    for forbidden in ["六神", "飞伏", "三合局", "应期", "八字旺衰", "大六壬四课三传"]:
        assert forbidden in prompt
    assert "不得把旺直接视为吉" in prompt
    assert "不得把死直接视为凶" in prompt


def test_liuyao_prompt_preserves_layered_useful_god_conflicts():
    prompt = PROMPT

    for text in ["近取诸身", "远取诸象", "layered", "ambiguous", "不能强行压成单一用神"]:
        assert text in prompt


def test_liuyao_prompt_requires_templates_and_six_spirits_as_auxiliary_only():
    prompt = PROMPT

    for text in ["question_template", "six_spirits", "辅助取象，不作主裁决", "青龙必吉", "白虎必凶", "玄武必欺瞒", "auxiliary_marks.enabled"]:
        assert text in prompt
    assert "不能单凭青龙断吉" in prompt
    assert "不能单凭白虎断凶" in prompt
    assert "不得编造其他神煞命中" in prompt


def test_liuyao_prompt_requires_spirit_roles_and_advanced_layer_order():
    prompt = PROMPT

    for text in ["spirit_role_analysis", "completion_chain", "advanced_layers", "原神", "忌神", "仇神", "闲神"]:
        assert text in prompt
    assert "先看用神，再看原神，再看忌神，再看仇神" in prompt
    assert "动爻必须先按 spirit_role 判断" in prompt
    assert "只有 advanced_layers.enabled 中的层可以作为证据" in prompt
    assert "不得输出具体公历日期" in prompt


def test_liuyao_prompt_requires_role_aware_twelve_stages():
    prompt = PROMPT

    for text in ["twelve_stage", "twelve_stage_analysis", "十二长生", "状态辅助，不直接定吉凶"]:
        assert text in prompt
    assert "十二长生必须先按 spirit_role 解释" in prompt
    assert "twelve_stages" in prompt


def test_liuyao_prompt_requires_role_aware_three_combination():
    prompt = PROMPT

    for text in ["combination_analysis", "三合", "role_impact"]:
        assert text in prompt
    assert "三合必须按 role_impact 解释" in prompt
    assert "不得单凭三合断吉凶" in prompt


def test_liuyao_prompt_requires_bounded_flying_hidden():
    prompt = PROMPT

    for text in ["flying_hidden_analysis", "飞伏", "不得编造伏神", "najia.hidden_spirits"]:
        assert text in prompt
    assert "不得输出具体公历日期" in prompt


def test_liuyao_prompt_requires_role_aware_advance_retreat():
    prompt = PROMPT

    for text in ["advance_retreat_analysis", "进退神", "用神进", "忌神进"]:
        assert text in prompt
    assert "应期只实现地支候选，不换算公历日期" in prompt


def test_liuyao_prompt_requires_bounded_timing_candidates():
    prompt = PROMPT

    for text in ["timing_analysis", "应期候选", "地支候选", "不得换算公历日期"]:
        assert text in prompt


def test_liuyao_prompt_requires_auxiliary_spirit_sha():
    prompt = PROMPT

    for text in ["spirit_sha_analysis", "天乙贵人", "驿马", "桃花", "神煞只作辅助"]:
        assert text in prompt
    assert "不得单凭神煞定成败" in prompt


def test_liuyao_prompt_requires_real_image_before_domain_translation():
    prompt = PROMPT

    for text in ["实象主证据", "先抓实象", "领域翻译", "行业先验"]:
        assert text in prompt
    assert "领域翻译只能解释六亲与爻象的语言" in prompt
    assert "不得用行业先验覆盖卦内证据" in prompt


def test_liuyao_prompt_requires_already_current_future_split():
    prompt = PROMPT

    for text in ["已然", "当前", "未然", "反转象"]:
        assert text in prompt
    assert "月建可表示占前或当月已经形成的背景" in prompt
    assert "日辰可表示眼前触发或近事变化" in prompt
    assert "静卦优先说明既成格局" in prompt
    assert "不得把月建生扶只读成未来必然有利" in prompt
