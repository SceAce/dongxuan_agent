import pytest

from dongxuan_agent.liuyao.hexagrams import (
    changed_binary,
    hexagram_by_name,
    parse_line_states,
    parse_named_hexagram,
)


def test_manual_line_states_parse_bottom_to_top():
    parsed = parse_line_states("少阳 老阴 少阴 少阳 老阳 少阴")

    assert [line.position for line in parsed] == [1, 2, 3, 4, 5, 6]
    assert "".join(line.yin_yang_binary for line in parsed) == "100110"
    assert [line.position for line in parsed if line.moving] == [2, 5]
    assert changed_binary(parsed) == "110100"


def test_line_state_count_error_mentions_bottom_to_top():
    with pytest.raises(ValueError, match="初爻.*上爻"):
        parse_line_states("少阳 老阴")


def test_line_state_name_error_lists_allowed_states():
    with pytest.raises(ValueError, match="少阳.*老阳.*少阴.*老阴"):
        parse_line_states("少阳 老阴 少阴 少阳 老阳 错误")


def test_hexagram_alias_li_zhi_dayou_derives_second_moving_line():
    parsed = parse_named_hexagram("离之大有")

    assert parsed.original.name == "离为火"
    assert parsed.changed.name == "火天大有"
    assert parsed.moving_lines == [2]
    assert parsed.original.binary_bottom_to_top == "101101"
    assert parsed.changed.binary_bottom_to_top == "111101"


def test_named_hexagram_with_explicit_moving_line_must_be_consistent():
    with pytest.raises(ValueError, match="不一致"):
        parse_named_hexagram("离卦三爻动得大有卦")


def test_unknown_hexagram_name_raises_clear_error():
    with pytest.raises(ValueError, match="未知卦名"):
        hexagram_by_name("不存在")
