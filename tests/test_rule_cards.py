from dongxuan_agent.rule_cards import build_rule_context, classify_question


def test_classify_question_by_common_issue_keywords():
    assert classify_question("最近身体健康怎么样") == "疾病健康"
    assert classify_question("这个感情还能复合吗") == "感情/婚恋"
    assert classify_question("今年工作能不能跳槽") == "事业/工作"
    assert classify_question("这笔投资财运如何") == "财运/交易"
    assert classify_question("考试能不能通过") == "考试/证书/申请"
    assert classify_question("丢的东西还能找回来吗") == "失物/寻人"
    assert classify_question("这次出行是否顺利") == "出行/迁移"
    assert classify_question("合同纠纷会不会走法律") == "官非/纠纷"
    assert classify_question("这个房子适合租吗") == "房宅/家宅"


def test_rule_context_includes_general_and_issue_cards():
    context = build_rule_context("合同纠纷会不会走法律")
    names = {card["name"] for card in context["cards"]}

    assert context["question_type"] == "官非/纠纷"
    assert "课盘结构优先" in names
    assert "神煞合参边界" in names
    assert "官符" in names
    assert "白虎/羊刃" in names
    assert all(card["avoid"] for card in context["cards"])
    assert all(card["sources"] for card in context["cards"])
