from __future__ import annotations

from .chart import HIDDEN_STEMS, BaziChart, ten_god


TEN_GOD_PATTERN = {
    "正官": "正官格",
    "七杀": "七杀格",
    "正印": "正印格",
    "偏印": "偏印格",
    "食神": "食神格",
    "伤官": "伤官格",
    "正财": "正财格",
    "偏财": "偏财格",
    "比肩": "比劫格",
    "劫财": "比劫格",
    "日主": "比劫格",
}

LU_BRANCH = {
    "甲": "寅",
    "乙": "卯",
    "丙": "巳",
    "丁": "午",
    "戊": "巳",
    "己": "午",
    "庚": "申",
    "辛": "酉",
    "壬": "亥",
    "癸": "子",
}

YANG_REN_BRANCH = {
    "甲": "卯",
    "丙": "午",
    "戊": "午",
    "庚": "酉",
    "壬": "子",
}


def analyze_pattern(chart: BaziChart) -> dict:
    payload = chart.to_dict()
    day_master = payload["day_master"]
    pillars = payload["pillars"]
    month = _pillar(pillars, "月柱")
    month_branch = month["branch"]
    month_hidden = HIDDEN_STEMS[month_branch]
    month_main_stem = month_hidden[0]
    candidate_patterns = _candidate_patterns(day_master, month_branch, month_hidden, pillars)
    primary = candidate_patterns[0]
    formation = _formation_evidence(day_master, month_branch, month_hidden, pillars, primary)
    damage = _damage_evidence(day_master, month, pillars, primary)
    return {
        "month_branch": month_branch,
        "month_main_stem": month_main_stem,
        "candidate_patterns": candidate_patterns,
        "primary_pattern": primary,
        "status": _status(primary, damage),
        "formation_evidence": formation,
        "damage_evidence": damage,
        "uncertainty": [
            "格局 V1 以月令本气取格为主，兼列月令藏干候选；尚未细判透清、会合变化、格局成败高低。",
            "建禄、羊刃 V1 只按月支识别候选，不直接替代扶抑、调候或用神判断。",
            "格局 V1 只输出结构证据，不定最终用神。",
        ],
    }


def _candidate_patterns(day_master: str, month_branch: str, month_hidden: tuple[str, ...], pillars: list[dict]) -> list[dict]:
    candidates = []
    for index, stem in enumerate(month_hidden):
        tg = ten_god(day_master, stem)
        candidates.append({
            "name": TEN_GOD_PATTERN[tg],
            "ten_god": tg,
            "stem": stem,
            "source": ("月令本气", "月令中气", "月令余气")[index],
            "confidence": "中" if index == 0 else "低",
            "evidence": f"月令{month_branch}藏{stem}，对日主为{tg}。",
        })
    if LU_BRANCH.get(day_master) == month_branch:
        candidates.insert(0, {
            "name": "建禄格",
            "ten_god": "比肩",
            "stem": day_master,
            "source": "月支禄地",
            "confidence": "中",
            "evidence": f"日主{day_master}禄在{month_branch}，列建禄格候选。",
        })
    if YANG_REN_BRANCH.get(day_master) == month_branch:
        candidates.insert(0, {
            "name": "羊刃格",
            "ten_god": "劫财",
            "stem": day_master,
            "source": "月支羊刃",
            "confidence": "中",
            "evidence": f"日主{day_master}羊刃在{month_branch}，列羊刃格候选。",
        })
    return _dedupe_patterns(candidates)


def _formation_evidence(
    day_master: str,
    month_branch: str,
    month_hidden: tuple[str, ...],
    pillars: list[dict],
    primary: dict,
) -> list[str]:
    month_main = month_hidden[0]
    evidence = [
        f"月令{month_branch}中{month_main}为{ten_god(day_master, month_main)}，故以{primary['name']}为第一候选。",
    ]
    visible = _visible_ten_gods(pillars)
    if primary["ten_god"] in visible:
        evidence.append(f"{primary['ten_god']}透出天干，格局气象较明。")
    useful_links = [tg for tg in ("正财", "偏财", "正官", "七杀", "正印", "偏印") if tg in visible]
    if useful_links:
        evidence.append("天干另见" + "、".join(useful_links) + "，可作为格局转化或配合线索。")
    return evidence


def _damage_evidence(day_master: str, month: dict, pillars: list[dict], primary: dict) -> list[str]:
    damage = []
    month_stem_tg = month["stem_ten_god"]
    if month_stem_tg in {"比肩", "劫财"} and primary["ten_god"] in {"正财", "偏财", "食神", "伤官"}:
        damage.append(f"月干{month['stem']}为{month_stem_tg}，对{primary['name']}有夺泄、争气或扰格之象。")
    if primary["ten_god"] in {"正官", "七杀"} and any(item["stem_ten_god"] == "伤官" for item in pillars):
        damage.append("天干见伤官，官杀格需防伤官冲官之扰。")
    if primary["ten_god"] in {"食神", "伤官"} and any(item["stem_ten_god"] in {"偏印", "正印"} for item in pillars):
        damage.append("天干见印，食伤格需辨印制食伤或成配合。")
    if not damage:
        damage.append("V1 未见明确破格证据；仍需结合透干清浊、合冲会局继续校验。")
    return damage


def _status(primary: dict, damage: list[str]) -> str:
    if primary["confidence"] == "低":
        return "格局待定"
    if any("扰" in item or "防" in item or "制" in item for item in damage):
        return "格局有扰"
    return "格局初成"


def _pillar(pillars: list[dict], name: str) -> dict:
    return next(item for item in pillars if item["name"] == name)


def _visible_ten_gods(pillars: list[dict]) -> set[str]:
    return {
        pillar["stem_ten_god"]
        for pillar in pillars
        if pillar["stem_ten_god"] != "日主"
    }


def _dedupe_patterns(candidates: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for item in candidates:
        key = (item["name"], item["source"])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
