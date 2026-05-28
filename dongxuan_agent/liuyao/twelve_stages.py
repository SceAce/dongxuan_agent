from __future__ import annotations


STAGE_ORDER = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

STAGE_BRANCHES = {
    "木": ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"],
    "火": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    "土": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
    "金": ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"],
    "水": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
}

STRENGTH_HINTS = {
    "长生": "growth",
    "沐浴": "unstable",
    "冠带": "growth",
    "临官": "growth",
    "帝旺": "peak",
    "衰": "decline",
    "病": "decline",
    "死": "cutoff",
    "墓": "storage",
    "绝": "cutoff",
    "胎": "incubation",
    "养": "incubation",
}

SUPPORTING_STAGES = {"长生", "冠带", "临官", "帝旺"}
BLOCKING_STAGES = {"死", "墓", "绝"}


def twelve_stage(element: str, branch: str) -> dict:
    branches = STAGE_BRANCHES[element]
    stage = STAGE_ORDER[branches.index(branch)]
    return {
        "stage": stage,
        "element": element,
        "branch": branch,
        "strength_hint": STRENGTH_HINTS[stage],
        "scope": "状态辅助，不直接定吉凶",
    }


def attach_twelve_stages(derived_lines: list[dict]) -> None:
    for line in derived_lines:
        line["twelve_stage"] = twelve_stage(line["element"], line["branch"])


def build_twelve_stage_analysis(derived_lines: list[dict]) -> dict:
    by_role = []
    supporting = []
    blocking = []
    mixed = []
    for line in derived_lines:
        stage = line["twelve_stage"]["stage"]
        role = line.get("spirit_role", "unresolved")
        item = {
            "position": line["position"],
            "six_relative": line["six_relative"],
            "spirit_role": role,
            "stage": stage,
            "strength_hint": line["twelve_stage"]["strength_hint"],
            "scope": "状态辅助，不直接定吉凶",
        }
        by_role.append(item)
        if stage in SUPPORTING_STAGES and role in {"useful_god", "original_spirit"}:
            supporting.append(
                {
                    "type": f"{role}_stage_support",
                    "line": line["position"],
                    "stage": stage,
                    "summary": f"{line['spirit_role_reason']}临{stage}，作为支持侧状态证据。",
                }
            )
        elif stage in SUPPORTING_STAGES and role in {"avoiding_spirit", "enemy_spirit"}:
            blocking.append(
                {
                    "type": f"{role}_stage_supports_obstruction",
                    "line": line["position"],
                    "stage": stage,
                    "summary": f"{line['spirit_role_reason']}临{stage}，作为阻断侧状态证据。",
                }
            )
        elif stage in BLOCKING_STAGES and role == "useful_god":
            blocking.append(
                {
                    "type": "useful_god_stage_block",
                    "line": line["position"],
                    "stage": stage,
                    "summary": f"用神临{stage}，作为用神状态受限证据。",
                }
            )
        elif stage in BLOCKING_STAGES and role == "original_spirit":
            mixed.append(
                {
                    "type": "original_spirit_stage_limited",
                    "line": line["position"],
                    "stage": stage,
                    "summary": f"原神临{stage}，生助来源状态受限。",
                }
            )
    return {
        "enabled": True,
        "scope": "状态辅助，不直接定吉凶",
        "by_role": by_role,
        "supporting_factors": supporting,
        "blocking_factors": blocking,
        "mixed_factors": mixed,
    }
