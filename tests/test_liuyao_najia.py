from dongxuan_agent.liuyao.hexagrams import HEXAGRAMS_BY_BINARY, hexagram_by_name
from dongxuan_agent.liuyao.najia import build_najia, palace_info


def test_li_hexagram_palace_shi_ying_and_generation():
    info = palace_info(hexagram_by_name("离为火"))

    assert info["palace"] == "离宫"
    assert info["palace_element"] == "火"
    assert info["generation"] == "本宫卦"
    assert info["shi_position"] == 6
    assert info["ying_position"] == 3


def test_dayou_palace_and_roles_are_available():
    info = palace_info(hexagram_by_name("火天大有"))

    assert info["palace"] == "乾宫"
    assert info["generation"] == "归魂卦"
    assert info["shi_position"] == 3
    assert info["ying_position"] == 6


def test_najia_uses_palace_element_not_day_master():
    payload = build_najia(hexagram_by_name("离为火"))

    assert payload["palace_element"] == "火"
    assert payload["lines"][0]["stem_branch"] == "己卯"
    assert payload["lines"][0]["branch"] == "卯"
    assert payload["lines"][0]["element"] == "木"
    assert payload["lines"][0]["six_relative"] == "父母"
    assert payload["lines"][2]["role"] == "应"
    assert payload["lines"][5]["role"] == "世"
    assert "day_master_element" not in payload


def test_missing_relative_gets_hidden_spirit_from_palace_pure_hexagram():
    payload = build_najia(hexagram_by_name("天地否"))

    assert payload["missing_relatives"] == ["子孙"]
    assert payload["hidden_spirits"] == [
        {
            "position": 1,
            "name": "初爻",
            "hidden_stem_branch": "甲子",
            "hidden_branch": "子",
            "hidden_element": "水",
            "hidden_six_relative": "子孙",
            "flying_stem_branch": "乙未",
            "flying_branch": "未",
            "flying_element": "土",
            "flying_six_relative": "父母",
            "source_palace_hexagram": "乾为天",
        }
    ]


def test_all_hexagrams_have_palace_info():
    for hexagram in HEXAGRAMS_BY_BINARY.values():
        info = palace_info(hexagram)

        assert info["palace"].endswith("宫")
        assert info["generation"]
        assert 1 <= info["shi_position"] <= 6
        assert 1 <= info["ying_position"] <= 6
