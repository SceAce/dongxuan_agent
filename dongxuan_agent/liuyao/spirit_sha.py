from __future__ import annotations


NOBLEMAN_BY_STEM = {
    "甲": ("丑", "未"),
    "戊": ("丑", "未"),
    "乙": ("子", "申"),
    "己": ("子", "申"),
    "丙": ("亥", "酉"),
    "丁": ("亥", "酉"),
    "庚": ("午", "寅"),
    "辛": ("午", "寅"),
    "壬": ("卯", "巳"),
    "癸": ("卯", "巳"),
}

HORSE_BY_BRANCH_GROUP = {
    ("申", "子", "辰"): "寅",
    ("寅", "午", "戌"): "申",
    ("亥", "卯", "未"): "巳",
    ("巳", "酉", "丑"): "亥",
}

PEACH_BY_BRANCH_GROUP = {
    ("申", "子", "辰"): "酉",
    ("寅", "午", "戌"): "卯",
    ("巳", "酉", "丑"): "午",
    ("亥", "卯", "未"): "子",
}

MEANINGS = {
    "天乙贵人": "贵人、扶助、转圜",
    "驿马": "行动、变动、远行、消息流动",
    "桃花": "吸引、人缘、情感、审美",
}


def build_spirit_sha_analysis(calendar: dict, derived_lines: list[dict]) -> dict:
    day_stem = calendar["day_gz"][0]
    day_branch = calendar["day_branch"]
    definitions = [
        ("天乙贵人", list(NOBLEMAN_BY_STEM[day_stem])),
        ("驿马", [_branch_group_value(day_branch, HORSE_BY_BRANCH_GROUP)]),
        ("桃花", [_branch_group_value(day_branch, PEACH_BY_BRANCH_GROUP)]),
    ]
    marks = [_mark(name, branches, derived_lines) for name, branches in definitions]
    _attach_marks(derived_lines, marks)
    return {
        "enabled": True,
        "scope": "神煞只作辅助取象与旁证，不作主裁决。",
        "marks": marks,
        "unresolved": [],
    }


def auxiliary_marks_payload() -> dict:
    return {
        "enabled": ["天乙贵人", "驿马", "桃花"],
        "reserved": ["华盖", "将星"],
        "scope": "神煞只作辅助取象与旁证，不作主裁决。",
    }


def _branch_group_value(day_branch: str, table: dict[tuple[str, str, str], str]) -> str:
    for branches, value in table.items():
        if day_branch in branches:
            return value
    raise RuntimeError(f"无法匹配日支神煞组：{day_branch}")


def _mark(name: str, branches: list[str], derived_lines: list[dict]) -> dict:
    matched = [
        {
            "position": line["position"],
            "name": line["name"],
            "branch": line["branch"],
            "six_relative": line["six_relative"],
            "spirit_role": line["spirit_role"],
            "moving": line["moving"],
        }
        for line in derived_lines
        if line["branch"] in branches
    ]
    return {
        "name": name,
        "branches": branches,
        "matched_lines": matched,
        "meaning": MEANINGS[name],
        "role_impacts": [_role_impact(name, line) for line in matched],
        "caution": "神煞不作主裁决，必须依附用神链和具体爻位。",
    }


def _role_impact(name: str, line: dict) -> dict:
    return {
        "position": line["position"],
        "spirit_role": line["spirit_role"],
        "impact": "auxiliary_only",
        "summary": f"{line['name']}临{name}，只作{MEANINGS[name]}旁证。",
    }


def _attach_marks(derived_lines: list[dict], marks: list[dict]) -> None:
    by_position: dict[int, list[dict]] = {line["position"]: [] for line in derived_lines}
    for mark in marks:
        for line in mark["matched_lines"]:
            by_position[line["position"]].append(
                {
                    "name": mark["name"],
                    "meaning": mark["meaning"],
                    "caution": mark["caution"],
                }
            )
    for line in derived_lines:
        line["spirit_sha_marks"] = by_position[line["position"]]
