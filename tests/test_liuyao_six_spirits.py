from dongxuan_agent.liuyao.six_spirits import assign_six_spirits


def test_ren_day_starts_with_xuanwu_from_initial_line():
    derived_lines = [
        {"position": 1, "six_relative": "父母", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": True, "moving": False},
        {"position": 2, "six_relative": "子孙", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": True},
        {"position": 3, "six_relative": "官鬼", "role": "应", "is_shi": False, "is_ying": True, "is_candidate_useful_god": True, "moving": False},
        {"position": 4, "six_relative": "妻财", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
        {"position": 5, "six_relative": "子孙", "role": None, "is_shi": False, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
        {"position": 6, "six_relative": "兄弟", "role": "世", "is_shi": True, "is_ying": False, "is_candidate_useful_god": False, "moving": False},
    ]

    result = assign_six_spirits("壬寅", derived_lines)

    assert result["day_stem"] == "壬"
    assert result["start_spirit"] == "玄武"
    assert [line["spirit"] for line in result["lines"]] == ["玄武", "青龙", "朱雀", "勾陈", "螣蛇", "白虎"]
    assert result["scope"] == "辅助取象，不作主裁决"
    assert result["lines"][0]["attached_to"]["six_relative"] == "父母"
    assert "不能单凭玄武断欺瞒" in result["lines"][0]["cautions"]
