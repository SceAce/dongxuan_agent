from __future__ import annotations


SIX_SPIRIT_ORDER = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]

START_BY_DAY_STEM = {
    "甲": "青龙",
    "乙": "青龙",
    "丙": "朱雀",
    "丁": "朱雀",
    "戊": "勾陈",
    "己": "螣蛇",
    "庚": "白虎",
    "辛": "白虎",
    "壬": "玄武",
    "癸": "玄武",
}

SIX_SPIRIT_IMAGERY = {
    "青龙": {"imagery": ["喜庆", "财喜", "文雅", "顺遂"], "cautions": ["不能单凭青龙断吉"]},
    "朱雀": {"imagery": ["口舌", "消息", "文书", "表达"], "cautions": ["需依附具体爻和六亲，不得单独断口舌"]},
    "勾陈": {"imagery": ["迟滞", "田土", "牵连", "旧事"], "cautions": ["不能单凭勾陈断拖延，需合看动静和月日"]},
    "螣蛇": {"imagery": ["虚惊", "疑虑", "缠绕", "怪异"], "cautions": ["不能单凭螣蛇断异常或欺诈"]},
    "白虎": {"imagery": ["伤病", "压力", "冲突", "急迫"], "cautions": ["不能单凭白虎断凶"]},
    "玄武": {"imagery": ["隐情", "暗昧", "欺瞒", "私下"], "cautions": ["不能单凭玄武断欺瞒"]},
}


def assign_six_spirits(day_gz: str, derived_lines: list[dict]) -> dict:
    day_stem = day_gz[0]
    start_spirit = START_BY_DAY_STEM[day_stem]
    start_index = SIX_SPIRIT_ORDER.index(start_spirit)
    lines = []
    for offset, line in enumerate(sorted(derived_lines, key=lambda item: item["position"])):
        spirit = SIX_SPIRIT_ORDER[(start_index + offset) % len(SIX_SPIRIT_ORDER)]
        info = SIX_SPIRIT_IMAGERY[spirit]
        lines.append(
            {
                "position": line["position"],
                "spirit": spirit,
                "imagery": list(info["imagery"]),
                "attached_to": {
                    "six_relative": line["six_relative"],
                    "role": line["role"],
                    "is_shi": line["is_shi"],
                    "is_ying": line["is_ying"],
                    "is_candidate_useful_god": line["is_candidate_useful_god"],
                    "moving": line["moving"],
                },
                "interpretation_scope": [
                    "只用于说明该爻象意呈现方式。",
                    "必须依附六亲、世应、用神、动变、旺衰字段使用。",
                ],
                "cautions": list(info["cautions"]),
            }
        )
    return {
        "start_basis": "按日干起六神",
        "day_stem": day_stem,
        "start_spirit": start_spirit,
        "scope": "辅助取象，不作主裁决",
        "lines": lines,
    }
