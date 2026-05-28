from dongxuan_agent.liuyao.imagery import build_imagery_context


def test_work_offer_contract_matches_official_and_parent_images():
    context = build_imagery_context("问工作 offer 合同什么时候下来", "事业/工作")

    relatives = {match["six_relative"] for match in context["matches"]}
    assert "官鬼" in relatives
    assert "父母" in relatives
    assert "工作" in context["tokens"]
    assert "合同" in context["tokens"]
    assert context["near_self_principle"].startswith("近取诸身")
    assert context["far_symbol_principle"].startswith("远取诸象")
