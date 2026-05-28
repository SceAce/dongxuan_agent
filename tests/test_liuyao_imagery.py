from dongxuan_agent.liuyao.imagery import build_imagery_context
from dongxuan_agent.liuyao import build_liuyao_chart


def test_work_offer_contract_matches_official_and_parent_images():
    context = build_imagery_context("问工作 offer 合同什么时候下来", "事业/工作")

    relatives = {match["six_relative"] for match in context["matches"]}
    assert "官鬼" in relatives
    assert "父母" in relatives
    assert "工作" in context["tokens"]
    assert "合同" in context["tokens"]
    assert context["near_self_principle"].startswith("近取诸身")
    assert context["far_symbol_principle"].startswith("远取诸象")


def test_work_offer_contract_selection_is_layered():
    payload = build_liuyao_chart(
        hexagram="离之大有",
        question="问工作 offer 合同什么时候下来",
        value="2026-05-28 09:30:00",
    ).to_dict()

    selection = payload["useful_god_selection"]
    assert selection["principle"] == "近取诸身，远取诸象"
    assert selection["selection_result"]["status"] == "layered"
    assert selection["selection_result"]["main_useful_god"] == "官鬼"
    assert "父母" in selection["selection_result"]["auxiliary_useful_gods"]
    assert selection["near_self_focus"][0]["role"] == "世"
    assert {item["six_relative"] for item in selection["far_symbol_focus"]} >= {"官鬼", "父母"}
    assert "不是互斥" in selection["conflicts"][0]["interpretation_hint"]
