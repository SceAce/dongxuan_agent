from __future__ import annotations

import re
from dataclasses import dataclass


LINE_NAMES = ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")


@dataclass(frozen=True)
class LineState:
    position: int
    name: str
    input_state: str
    yin_yang: str
    yin_yang_binary: str
    moving: bool
    changed_yin_yang: str
    changed_binary: str


@dataclass(frozen=True)
class Hexagram:
    name: str
    short_name: str
    upper_trigram: str
    lower_trigram: str
    binary_bottom_to_top: str


@dataclass(frozen=True)
class NamedHexagramInput:
    original: Hexagram
    changed: Hexagram
    moving_lines: list[int]


LINE_STATE_RULES = {
    "少阳": ("阳", "1", False, "阳", "1"),
    "老阳": ("阳", "1", True, "阴", "0"),
    "少阴": ("阴", "0", False, "阴", "0"),
    "老阴": ("阴", "0", True, "阳", "1"),
}

TRIGRAMS = {
    "乾": ("天", "111"),
    "兑": ("泽", "110"),
    "离": ("火", "101"),
    "震": ("雷", "100"),
    "巽": ("风", "011"),
    "坎": ("水", "010"),
    "艮": ("山", "001"),
    "坤": ("地", "000"),
}

HEXAGRAM_SHORT_NAMES = {
    ("乾", "乾"): "乾",
    ("坤", "坤"): "坤",
    ("坎", "震"): "屯",
    ("艮", "坎"): "蒙",
    ("坎", "乾"): "需",
    ("乾", "坎"): "讼",
    ("坤", "坎"): "师",
    ("坎", "坤"): "比",
    ("巽", "乾"): "小畜",
    ("乾", "兑"): "履",
    ("坤", "乾"): "泰",
    ("乾", "坤"): "否",
    ("乾", "离"): "同人",
    ("离", "乾"): "大有",
    ("坤", "艮"): "谦",
    ("震", "坤"): "豫",
    ("兑", "震"): "随",
    ("艮", "巽"): "蛊",
    ("坤", "兑"): "临",
    ("巽", "坤"): "观",
    ("离", "震"): "噬嗑",
    ("艮", "离"): "贲",
    ("艮", "坤"): "剥",
    ("坤", "震"): "复",
    ("乾", "震"): "无妄",
    ("艮", "乾"): "大畜",
    ("艮", "震"): "颐",
    ("兑", "巽"): "大过",
    ("坎", "坎"): "坎",
    ("离", "离"): "离",
    ("兑", "艮"): "咸",
    ("震", "巽"): "恒",
    ("乾", "艮"): "遁",
    ("震", "乾"): "大壮",
    ("离", "坤"): "晋",
    ("坤", "离"): "明夷",
    ("巽", "离"): "家人",
    ("离", "兑"): "睽",
    ("坎", "艮"): "蹇",
    ("震", "坎"): "解",
    ("艮", "兑"): "损",
    ("巽", "震"): "益",
    ("兑", "乾"): "夬",
    ("乾", "巽"): "姤",
    ("兑", "坤"): "萃",
    ("坤", "巽"): "升",
    ("兑", "坎"): "困",
    ("坎", "巽"): "井",
    ("兑", "离"): "革",
    ("离", "巽"): "鼎",
    ("震", "震"): "震",
    ("艮", "艮"): "艮",
    ("巽", "艮"): "渐",
    ("震", "兑"): "归妹",
    ("震", "离"): "丰",
    ("离", "艮"): "旅",
    ("巽", "巽"): "巽",
    ("兑", "兑"): "兑",
    ("巽", "坎"): "涣",
    ("坎", "兑"): "节",
    ("巽", "兑"): "中孚",
    ("震", "艮"): "小过",
    ("坎", "离"): "既济",
    ("离", "坎"): "未济",
}


def _normalize_hexagram_name(name: str) -> str:
    return name.strip().replace("卦", "")


def _build_hexagrams() -> tuple[dict[str, Hexagram], dict[str, Hexagram]]:
    by_binary: dict[str, Hexagram] = {}
    by_alias: dict[str, Hexagram] = {}
    for upper, (upper_image, upper_binary) in TRIGRAMS.items():
        for lower, (lower_image, lower_binary) in TRIGRAMS.items():
            short_name = HEXAGRAM_SHORT_NAMES[(upper, lower)]
            full_name = f"{upper}为{upper_image}" if upper == lower else f"{upper_image}{lower_image}{short_name}"
            binary = lower_binary + upper_binary
            hexagram = Hexagram(
                name=full_name,
                short_name=short_name,
                upper_trigram=upper,
                lower_trigram=lower,
                binary_bottom_to_top=binary,
            )
            by_binary[binary] = hexagram
            aliases = {full_name, short_name, full_name.replace("为", "")}
            if upper == lower:
                aliases.add(upper)
                aliases.add(f"{upper}卦")
            for alias in aliases:
                by_alias[_normalize_hexagram_name(alias)] = hexagram
    return by_binary, by_alias


HEXAGRAMS_BY_BINARY, HEXAGRAMS_BY_ALIAS = _build_hexagrams()


def parse_line_states(raw: str) -> list[LineState]:
    states = [part for part in re.split(r"[\s,，、]+", raw.strip()) if part]
    if len(states) != 6:
        raise ValueError("六爻结果必须正好六个，并按 初爻、二爻、三爻、四爻、五爻、上爻 自下而上输入。")
    lines: list[LineState] = []
    for index, state in enumerate(states, start=1):
        if state not in LINE_STATE_RULES:
            allowed = "、".join(LINE_STATE_RULES)
            raise ValueError(f"未知爻态：{state}。允许值：{allowed}。")
        yin_yang, binary, moving, changed_yin_yang, changed = LINE_STATE_RULES[state]
        lines.append(
            LineState(
                position=index,
                name=LINE_NAMES[index - 1],
                input_state=state,
                yin_yang=yin_yang,
                yin_yang_binary=binary,
                moving=moving,
                changed_yin_yang=changed_yin_yang,
                changed_binary=changed,
            )
        )
    return lines


def changed_binary(lines: list[LineState]) -> str:
    return "".join(line.changed_binary for line in lines)


def hexagram_by_name(name: str) -> Hexagram:
    key = _normalize_hexagram_name(name)
    try:
        return HEXAGRAMS_BY_ALIAS[key]
    except KeyError as exc:
        raise ValueError(f"未知卦名：{name}") from exc


def hexagram_by_binary(binary_bottom_to_top: str) -> Hexagram:
    try:
        return HEXAGRAMS_BY_BINARY[binary_bottom_to_top]
    except KeyError as exc:
        raise ValueError(f"未知卦象二进制：{binary_bottom_to_top}") from exc


def parse_named_hexagram(raw: str) -> NamedHexagramInput:
    text = raw.strip().replace(" ", "")
    explicit_line = _parse_explicit_moving_line(text)
    if "之" in text:
        left, right = text.split("之", 1)
        original = hexagram_by_name(_clean_hexagram_part(left))
        changed = hexagram_by_name(_clean_hexagram_part(right))
    elif "得" in text:
        left, right = text.split("得", 1)
        original = hexagram_by_name(_clean_hexagram_part(left))
        changed = hexagram_by_name(_clean_hexagram_part(right))
    else:
        raise ValueError("命名卦输入需包含“之”或“得”，例如：离之大有。")

    moving_lines = _moving_lines_between(original.binary_bottom_to_top, changed.binary_bottom_to_top)
    if explicit_line is not None and moving_lines != [explicit_line]:
        raise ValueError(f"动爻与变卦不一致：输入为{explicit_line}爻动，实际差异为{moving_lines}。")
    return NamedHexagramInput(original=original, changed=changed, moving_lines=moving_lines)


def line_states_from_hexagrams(original: Hexagram, moving_lines: list[int]) -> list[LineState]:
    states = []
    for index, bit in enumerate(original.binary_bottom_to_top, start=1):
        moving = index in moving_lines
        if bit == "1":
            states.append("老阳" if moving else "少阳")
        else:
            states.append("老阴" if moving else "少阴")
    return parse_line_states(" ".join(states))


def _moving_lines_between(original_binary: str, changed: str) -> list[int]:
    return [index for index, (left, right) in enumerate(zip(original_binary, changed), start=1) if left != right]


def _parse_explicit_moving_line(text: str) -> int | None:
    match = re.search(r"([初二三四五上123456])爻动", text)
    if not match:
        return None
    token = match.group(1)
    text_positions = {"初": 1, "二": 2, "三": 3, "四": 4, "五": 5, "上": 6}
    if token in text_positions:
        return text_positions[token]
    return int(token)


def _clean_hexagram_part(value: str) -> str:
    cleaned = re.sub(r"[初二三四五上123456]爻动?", "", value)
    return cleaned.replace("卦", "").replace("动", "")
