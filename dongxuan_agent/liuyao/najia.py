from __future__ import annotations

from .hexagrams import Hexagram


BRANCH_ELEMENTS = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

PALACE_ELEMENTS = {
    "乾": "金",
    "兑": "金",
    "离": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "艮": "土",
    "坤": "土",
}

GENERATING = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

CONTROLLING = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}

NAJIA_BY_TRIGRAM = {
    "乾": {
        "lower": ("甲子", "甲寅", "甲辰"),
        "upper": ("壬午", "壬申", "壬戌"),
    },
    "坤": {
        "lower": ("乙未", "乙巳", "乙卯"),
        "upper": ("癸丑", "癸亥", "癸酉"),
    },
    "震": {
        "lower": ("庚子", "庚寅", "庚辰"),
        "upper": ("庚午", "庚申", "庚戌"),
    },
    "巽": {
        "lower": ("辛丑", "辛亥", "辛酉"),
        "upper": ("辛未", "辛巳", "辛卯"),
    },
    "坎": {
        "lower": ("戊寅", "戊辰", "戊午"),
        "upper": ("戊申", "戊戌", "戊子"),
    },
    "离": {
        "lower": ("己卯", "己丑", "己亥"),
        "upper": ("己酉", "己未", "己巳"),
    },
    "艮": {
        "lower": ("丙辰", "丙午", "丙申"),
        "upper": ("丙戌", "丙子", "丙寅"),
    },
    "兑": {
        "lower": ("丁巳", "丁卯", "丁丑"),
        "upper": ("丁亥", "丁酉", "丁未"),
    },
}

PALACE_SEQUENCES = {
    "乾": ("乾", "姤", "遁", "否", "观", "剥", "晋", "大有"),
    "兑": ("兑", "困", "萃", "咸", "蹇", "谦", "小过", "归妹"),
    "离": ("离", "旅", "鼎", "未济", "蒙", "涣", "讼", "同人"),
    "震": ("震", "豫", "解", "恒", "升", "井", "大过", "随"),
    "巽": ("巽", "小畜", "家人", "益", "无妄", "噬嗑", "颐", "蛊"),
    "坎": ("坎", "节", "屯", "既济", "革", "丰", "明夷", "师"),
    "艮": ("艮", "贲", "大畜", "损", "睽", "履", "中孚", "渐"),
    "坤": ("坤", "复", "临", "泰", "大壮", "夬", "需", "比"),
}

GENERATIONS = ("本宫卦", "一世卦", "二世卦", "三世卦", "四世卦", "五世卦", "游魂卦", "归魂卦")

SHI_YING_BY_GENERATION = {
    "本宫卦": (6, 3),
    "一世卦": (1, 4),
    "二世卦": (2, 5),
    "三世卦": (3, 6),
    "四世卦": (4, 1),
    "五世卦": (5, 2),
    "游魂卦": (4, 1),
    "归魂卦": (3, 6),
}


def palace_info(hexagram: Hexagram) -> dict:
    table = _palace_table()
    try:
        return dict(table[hexagram.binary_bottom_to_top])
    except KeyError as exc:
        raise RuntimeError(f"缺少八宫映射：{hexagram.binary_bottom_to_top}") from exc


def build_najia(hexagram: Hexagram) -> dict:
    palace = palace_info(hexagram)
    palace_element = palace["palace_element"]
    lower = NAJIA_BY_TRIGRAM[hexagram.lower_trigram]["lower"]
    upper = NAJIA_BY_TRIGRAM[hexagram.upper_trigram]["upper"]
    stem_branches = lower + upper
    lines = []
    for position, stem_branch in enumerate(stem_branches, start=1):
        branch = stem_branch[1]
        role = None
        if position == palace["shi_position"]:
            role = "世"
        elif position == palace["ying_position"]:
            role = "应"
        lines.append(
            {
                "position": position,
                "stem_branch": stem_branch,
                "branch": branch,
                "element": BRANCH_ELEMENTS[branch],
                "six_relative": six_relative(palace_element, BRANCH_ELEMENTS[branch]),
                "role": role,
            }
        )
    present = {line["six_relative"] for line in lines}
    missing_relatives = [name for name in ("兄弟", "子孙", "妻财", "官鬼", "父母") if name not in present]
    return {
        "palace_element": palace_element,
        "lines": lines,
        "missing_relatives": missing_relatives,
        "hidden_spirits": _hidden_spirits(lines, missing_relatives, palace),
    }


def six_relative(self_element: str, other_element: str) -> str:
    if other_element == self_element:
        return "兄弟"
    if GENERATING[self_element] == other_element:
        return "子孙"
    if GENERATING[other_element] == self_element:
        return "父母"
    if CONTROLLING[self_element] == other_element:
        return "妻财"
    if CONTROLLING[other_element] == self_element:
        return "官鬼"
    raise ValueError(f"无法推导六亲：{self_element=} {other_element=}")


def _palace_table() -> dict[str, dict]:
    table: dict[str, dict] = {}
    for palace_trigram, names in PALACE_SEQUENCES.items():
        for generation, name in zip(GENERATIONS, names):
            hexagram = _hexagram_by_short_name(name)
            binary = hexagram.binary_bottom_to_top
            shi, ying = SHI_YING_BY_GENERATION[generation]
            table[binary] = {
                "palace": f"{palace_trigram}宫",
                "palace_element": PALACE_ELEMENTS[palace_trigram],
                "generation": generation,
                "shi_position": shi,
                "ying_position": ying,
                "shi_line": _line_name(shi),
                "ying_line": _line_name(ying),
                "hexagram_name": hexagram.name,
            }
    if len(table) != 64:
        raise RuntimeError(f"八宫映射数量错误：{len(table)}")
    return table


def _hexagram_by_short_name(name: str) -> Hexagram:
    from .hexagrams import hexagram_by_name

    return hexagram_by_name(name)


def _hidden_spirits(visible_lines: list[dict], missing_relatives: list[str], palace: dict) -> list[dict]:
    if not missing_relatives:
        return []
    palace_trigram = palace["palace"].replace("宫", "")
    pure_hexagram = _hexagram_by_short_name(palace_trigram)
    pure_stem_branches = (
        NAJIA_BY_TRIGRAM[pure_hexagram.lower_trigram]["lower"]
        + NAJIA_BY_TRIGRAM[pure_hexagram.upper_trigram]["upper"]
    )
    visible_by_position = {line["position"]: line for line in visible_lines}
    hidden = []
    for position, stem_branch in enumerate(pure_stem_branches, start=1):
        branch = stem_branch[1]
        hidden_element = BRANCH_ELEMENTS[branch]
        hidden_relative = six_relative(palace["palace_element"], hidden_element)
        if hidden_relative not in missing_relatives:
            continue
        flying = visible_by_position[position]
        hidden.append(
            {
                "position": position,
                "name": _line_name(position),
                "hidden_stem_branch": stem_branch,
                "hidden_branch": branch,
                "hidden_element": hidden_element,
                "hidden_six_relative": hidden_relative,
                "flying_stem_branch": flying["stem_branch"],
                "flying_branch": flying["branch"],
                "flying_element": flying["element"],
                "flying_six_relative": flying["six_relative"],
                "source_palace_hexagram": pure_hexagram.name,
            }
        )
    return hidden


def _line_name(position: int) -> str:
    return ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")[position - 1]
