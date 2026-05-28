from dongxuan_agent.liuyao import build_liuyao_chart


def test_spirit_sha_marks_are_auxiliary_and_attached_to_lines():
    payload = build_liuyao_chart(
        hexagram="晋之大有",
        question="问工作能否推进",
        value="2026-05-28 09:30:00",
    ).to_dict()

    analysis = payload["spirit_sha_analysis"]

    assert analysis["enabled"] is True
    assert analysis["scope"] == "神煞只作辅助取象与旁证，不作主裁决。"
    marks = {mark["name"]: mark for mark in analysis["marks"]}
    assert marks["天乙贵人"]["branches"] == ["卯", "巳"]
    assert marks["驿马"]["branches"] == ["申"]
    assert marks["桃花"]["branches"] == ["卯"]
    assert payload["auxiliary_marks"]["enabled"] == ["天乙贵人", "驿马", "桃花"]
    assert any(line["spirit_sha_marks"] for line in payload["derived_lines"])
