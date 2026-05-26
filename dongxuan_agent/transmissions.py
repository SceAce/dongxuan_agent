from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .constants import (
    BRANCH_ELEMENTS,
    BRANCH_OPPOSITE,
    BRANCH_PUNISH,
    BRANCH_THREE_COMBINE,
    BRANCH_YINYANG,
    BRANCHES,
    CONTROLLING,
    STEM_COMBINE_BRANCH,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
    STEM_YINYANG,
)


class LessonLike(Protocol):
    name: str
    lower: str
    upper: str
    relation: str
    lower_branch: str


@dataclass(frozen=True)
class KeCandidate:
    lesson: LessonLike
    kind: str


@dataclass(frozen=True)
class Transmissions:
    items: tuple[str | None, str | None, str | None]
    status: str
    method: str
    note: str


def rotate_from(branch: str) -> list[str]:
    idx = BRANCHES.index(branch)
    return list(BRANCHES[idx:] + BRANCHES[:idx])


def build_transmissions(lessons: tuple[LessonLike, LessonLike, LessonLike, LessonLike], heaven_plate: dict[str, str]) -> Transmissions:
    day_stem = lessons[0].lower
    day_branch = lessons[2].lower
    day_gz = day_stem + day_branch
    if all(earth == heaven for earth, heaven in heaven_plate.items()):
        first = lessons[0].upper if lessons[0].relation in {"上克下", "下贼上"} else (lessons[0].upper if STEM_YINYANG[day_stem] == "阳" else lessons[2].upper)
        second = BRANCH_PUNISH[first]
        third = BRANCH_PUNISH[second] if second != BRANCH_PUNISH[second] else BRANCH_OPPOSITE[second]
        return Transmissions((first, second, third), "complete", "伏吟", "天地盘伏吟；有克取克，无克刚日取日上、柔日取辰上，并递刑为中末。")

    if all(heaven_plate[earth] == BRANCH_OPPOSITE[earth] for earth in BRANCHES):
        ke = _ke_candidate_details(lessons)
        if ke:
            return _choose_fanyin_with_ke(day_stem, ke, heaven_plate)
        return _choose_fanyin_without_ke(day_branch, lessons)

    ke = _ke_candidate_details(lessons)
    if ke:
        return _choose_from_ke_details(day_stem, ke, heaven_plate, "贼克")

    if day_gz in {"丁未", "癸丑", "甲寅", "己未", "庚申"}:
        return _choose_bazhuan(day_stem, lessons)

    remote = _remote_ke(day_stem, lessons)
    if remote:
        first = _choose_by_yinyang(day_stem, remote)
        return Transmissions(_chain(first, heaven_plate), "complete", "遥克", "四课无上下克，取神遥克日或日遥克神，复多则比用。")

    unique_lowers = {lesson.lower for lesson in lessons}
    if len(unique_lowers) == 3:
        first = heaven_plate[STEM_COMBINE_BRANCH[day_stem]] if STEM_YINYANG[day_stem] == "阳" else heaven_plate[BRANCH_THREE_COMBINE[day_branch][0]]
        return Transmissions((first, lessons[0].upper, lessons[0].upper), "complete", "别责", "四课不全三课备且无克无遥，刚取干合上神，柔取支三合上神，中末归日上。")

    first = heaven_plate["酉"] if STEM_YINYANG[day_stem] == "阳" else next(earth for earth, heaven in heaven_plate.items() if heaven == "酉")
    second = lessons[2].upper if STEM_YINYANG[day_stem] == "阳" else lessons[0].upper
    third = lessons[0].upper if STEM_YINYANG[day_stem] == "阳" else lessons[2].upper
    return Transmissions((first, second, third), "complete", "昴星", "四课无上下克、无遥克，刚日仰视酉上，柔日俯视酉临，中末取辰上日上。")


def _chain(first: str, heaven_plate: dict[str, str]) -> tuple[str, str, str]:
    second = heaven_plate[first]
    third = heaven_plate[second]
    return first, second, third


def _fanyin_chain(first: str, heaven_plate: dict[str, str]) -> tuple[str, str, str]:
    second = BRANCH_OPPOSITE[first]
    third = heaven_plate[first]
    return first, second, third


def _choose_fanyin_with_ke(day_stem: str, candidates: list[KeCandidate], heaven_plate: dict[str, str]) -> Transmissions:
    base = _choose_from_ke_details(day_stem, candidates, heaven_plate, "返吟")
    first = base.items[0]
    if first is None:
        return base
    return Transmissions(
        _fanyin_chain(first, heaven_plate),
        base.status,
        base.method,
        f"返吟有克，初传按{base.method}取{first}，中取初冲，末取初上。",
    )


def _choose_fanyin_without_ke(day_branch: str, lessons: tuple[LessonLike, LessonLike, LessonLike, LessonLike]) -> Transmissions:
    first = _horse(day_branch)
    return Transmissions((first, lessons[2].upper, lessons[0].upper), "complete", "返吟", f"返吟无克，取日支驿马{first}为初传，中传取支上{lessons[2].upper}，末传取干上{lessons[0].upper}。")


def _horse(branch: str) -> str:
    if branch in "申子辰":
        return "寅"
    if branch in "寅午戌":
        return "申"
    if branch in "巳酉丑":
        return "亥"
    return "巳"


def _choose_bazhuan(day_stem: str, lessons: tuple[LessonLike, LessonLike, LessonLike, LessonLike]) -> Transmissions:
    if STEM_YINYANG[day_stem] == "阳":
        base = lessons[0].upper
        first = rotate_from(base)[2]
    else:
        base = lessons[3].upper
        first = rotate_from(base)[-2]
    return Transmissions((first, lessons[0].upper, lessons[0].upper), "complete", "八专", "八专日无上下克，不取遥克；刚日从日上顺数三，柔日从支阴逆数三，中末归日上。")


def _ke_candidate_details(lessons: tuple[LessonLike, LessonLike, LessonLike, LessonLike]) -> list[KeCandidate]:
    ordered = [KeCandidate(lesson, "下贼上") for lesson in lessons if lesson.relation == "下贼上"]
    if not ordered:
        ordered = [KeCandidate(lesson, "上克下") for lesson in lessons if lesson.relation == "上克下"]
    unique: list[KeCandidate] = []
    seen = set()
    for candidate in ordered:
        if candidate.lesson.upper not in seen:
            unique.append(candidate)
            seen.add(candidate.lesson.upper)
    return unique


def _choose_by_yinyang(day_stem: str, candidates: list[str]) -> str:
    day_yy = STEM_YINYANG[day_stem]
    matching = [item for item in candidates if BRANCH_YINYANG[item] == day_yy]
    return matching[0] if matching else candidates[0]


def _choose_from_ke_details(day_stem: str, candidates: list[KeCandidate], heaven_plate: dict[str, str], default_method: str) -> Transmissions:
    if len(candidates) == 1:
        first = candidates[0].lesson.upper
        return Transmissions(_chain(first, heaven_plate), "complete", default_method, "四课中仅一处克贼，取其上神为初传，中末相因。")
    same = [candidate for candidate in candidates if BRANCH_YINYANG[candidate.lesson.upper] == STEM_YINYANG[day_stem]]
    if len(same) == 1:
        first = same[0].lesson.upper
        return Transmissions(_chain(first, heaven_plate), "complete", "比用", "克贼多见，取与日干阴阳相比者为用。")
    shehai_candidates = same if same else candidates
    first, note = _choose_by_shehai(shehai_candidates)
    return Transmissions(_chain(first, heaven_plate), "complete", "涉害", note)


def _choose_by_shehai(candidates: list[KeCandidate]) -> tuple[str, str]:
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            _shehai_score(candidate),
            _palace_rank(candidate.lesson.lower_branch),
            -candidates.index(candidate),
        ),
        reverse=True,
    )
    selected = ranked[0]
    parts = [
        f"{candidate.lesson.upper}临{candidate.lesson.lower_branch}得{_shehai_score(candidate)}"
        for candidate in candidates
    ]
    return selected.lesson.upper, f"克贼多见且比用不唯一，按涉害归本深浅取用；{ '，'.join(parts) }，取{selected.lesson.upper}为初传。"


def _shehai_score(candidate: KeCandidate) -> int:
    upper = candidate.lesson.upper
    score = 0
    for branch in _path_to_home(candidate.lesson.lower_branch, upper):
        branch_element = BRANCH_ELEMENTS[branch]
        lodged_stems = [stem for stem, lodging in STEM_LODGING_BRANCH.items() if lodging == branch]
        if candidate.kind == "上克下":
            if CONTROLLING[BRANCH_ELEMENTS[upper]] == branch_element:
                score += 1
            score += sum(1 for stem in lodged_stems if CONTROLLING[BRANCH_ELEMENTS[upper]] == STEM_ELEMENTS[stem])
        else:
            if CONTROLLING[branch_element] == BRANCH_ELEMENTS[upper]:
                score += 1
            score += sum(1 for stem in lodged_stems if CONTROLLING[STEM_ELEMENTS[stem]] == BRANCH_ELEMENTS[upper])
    return score


def _path_to_home(start: str, home: str) -> list[str]:
    path = []
    current = start
    while True:
        path.append(current)
        if current == home:
            return path
        current = BRANCHES[(BRANCHES.index(current) + 1) % len(BRANCHES)]


def _palace_rank(branch: str) -> int:
    if branch in "寅申巳亥":
        return 3
    if branch in "子午卯酉":
        return 2
    return 1


def _remote_ke(day_stem: str, lessons: tuple[LessonLike, LessonLike, LessonLike, LessonLike]) -> list[str]:
    stem_el = STEM_ELEMENTS[day_stem]
    uppers = []
    for lesson in lessons:
        if lesson.upper not in uppers:
            uppers.append(lesson.upper)
    remote = [item for item in uppers if CONTROLLING[BRANCH_ELEMENTS[item]] == stem_el]
    if remote:
        return remote
    return [item for item in uppers if CONTROLLING[stem_el] == BRANCH_ELEMENTS[item]]
