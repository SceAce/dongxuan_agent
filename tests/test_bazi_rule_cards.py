from dongxuan_agent.bazi_rule_cards import build_bazi_rule_context


REQUIRED_CARD_FIELDS = {
    "name",
    "meaning",
    "use_when",
    "avoid",
    "sources",
    "implemented",
}


def test_bazi_rule_context_returns_general_and_year_event_cards():
    context = build_bazi_rule_context(question="推断2025年发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}

    assert context["mode"] == "year_event"
    assert context["target_year"] == 2025
    assert context["selection_rule"]
    assert "原局结构优先" in names
    assert "流年引动" in names
    assert "大运流年合参" in names
    assert all(REQUIRED_CARD_FIELDS <= card.keys() for card in context["cards"])
    assert all(card["meaning"] for card in context["cards"])
    assert all(card["use_when"] for card in context["cards"])
    assert all(card["avoid"] for card in context["cards"])
    assert all(card["sources"] for card in context["cards"])
    assert all(card["implemented"] is True for card in context["cards"])


def test_bazi_rule_context_includes_event_domain_cards():
    context = build_bazi_rule_context(question="2025年学业和感情发生了什么", target_year=2025)
    names = {card["name"] for card in context["cards"]}

    assert "学业/考试取象" in names
    assert "感情/关系取象" in names
    assert "财务/资源取象" in names


def test_bazi_rule_context_uses_chart_structure_mode_without_target_year():
    context = build_bazi_rule_context(question=None, target_year=None)
    names = {card["name"] for card in context["cards"]}

    assert context["mode"] == "chart_structure"
    assert context["target_year"] is None
    assert {"原局结构优先", "流年引动", "大运流年合参"} <= names
    assert "学业/考试取象" not in names
    assert "财务/资源取象" not in names


def test_bazi_rule_context_matches_domain_keyword_variants():
    context = build_bazi_rule_context(question="考试、证书、钱和资源怎么判断", target_year=None)
    names = {card["name"] for card in context["cards"]}

    assert "学业/考试取象" in names
    assert "财务/资源取象" in names
    assert "感情/关系取象" not in names
