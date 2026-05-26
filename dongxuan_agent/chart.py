from __future__ import annotations

from dataclasses import dataclass

from .calendar_engine import CalendarInfo, get_calendar_info
from .constants import (
    BRANCH_ELEMENTS,
    BRANCHES,
    CONTROLLING,
    DAY_NOBLEMAN,
    GENERATING,
    HEAVENLY_GENERALS,
    HEAVENLY_OFFICER_NAMES,
    STEM_ELEMENTS,
    STEM_LODGING_BRANCH,
)
from .spirits import build_spirit_sha
from .transmissions import Transmissions, build_transmissions
from .xun import build_xun_dun
from .season import season_state


@dataclass(frozen=True)
class Lesson:
    name: str
    lower: str
    upper: str
    relation: str
    lower_branch: str


@dataclass(frozen=True)
class DaliurenChart:
    calendar: CalendarInfo
    month_general: str
    heaven_plate: dict[str, str]
    earth_plate: tuple[str, ...]
    four_lessons: tuple[Lesson, Lesson, Lesson, Lesson]
    transmissions: Transmissions
    transmission_details: tuple[dict[str, str | None], dict[str, str | None], dict[str, str | None]]
    xun_dun: dict
    lesson_bodies: tuple[dict[str, str], ...]
    brief_analysis: str
    nobleman: dict[str, str]
    heavenly_generals: dict[str, str]
    heavenly_officers: dict[str, dict[str, str]]
    six_relatives: dict[str, dict[str, str]]
    spirit_sha: dict
    xunkong: tuple[str, str]
    uncertainty: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "calendar": {
                "datetime": self.calendar.dt.isoformat(),
                "timezone": self.calendar.timezone,
                "year_gz": self.calendar.year_gz,
                "month_gz": self.calendar.month_gz,
                "day_gz": self.calendar.day_gz,
                "hour_gz": self.calendar.hour_gz,
                "hour_branch": self.calendar.hour_branch,
            },
            "month_general": self.month_general,
            "heaven_plate": self.heaven_plate,
            "four_lessons": [lesson.__dict__ for lesson in self.four_lessons],
            "transmissions": self.transmissions.__dict__,
            "transmission_details": self.transmission_details,
            "xun_dun": self.xun_dun,
            "lesson_bodies": self.lesson_bodies,
            "brief_analysis": self.brief_analysis,
            "nobleman": self.nobleman,
            "heavenly_generals": self.heavenly_generals,
            "heavenly_officers": self.heavenly_officers,
            "six_relatives": self.six_relatives,
            "spirit_sha": self.spirit_sha,
            "xunkong": self.xunkong,
            "uncertainty": list(self.uncertainty),
        }


def rotate_from(branch: str) -> list[str]:
    idx = BRANCHES.index(branch)
    return list(BRANCHES[idx:] + BRANCHES[:idx])


def build_heaven_plate(month_general: str, hour_branch: str) -> dict[str, str]:
    earth = rotate_from(hour_branch)
    heaven = rotate_from(month_general)
    return dict(zip(earth, heaven, strict=True))


def relation(upper: str, lower: str) -> str:
    upper_el = BRANCH_ELEMENTS.get(upper) or STEM_ELEMENTS[upper]
    lower_el = BRANCH_ELEMENTS.get(lower) or STEM_ELEMENTS[lower]
    if upper_el == lower_el:
        return "比和"
    if CONTROLLING[upper_el] == lower_el:
        return "上克下"
    if CONTROLLING[lower_el] == upper_el:
        return "下贼上"
    return "相生/无克"


def upper_of(heaven_plate: dict[str, str], lower: str) -> str:
    if lower in heaven_plate:
        return heaven_plate[lower]
    # Ten stems do not sit on the earth plate in this simplified V1 model.
    # Use the day branch proxy only when calculating lesson one lower stem relation.
    raise KeyError(lower)


def build_four_lessons(calendar: CalendarInfo, heaven_plate: dict[str, str]) -> tuple[Lesson, Lesson, Lesson, Lesson]:
    day_stem = calendar.day_gz[0]
    day_branch = calendar.day_gz[1]
    stem_lodging = STEM_LODGING_BRANCH[day_stem]
    first_upper = heaven_plate[stem_lodging]
    second_upper = heaven_plate[first_upper]
    third_upper = heaven_plate[day_branch]
    fourth_upper = heaven_plate[third_upper]
    return (
        Lesson("一课", day_stem, first_upper, relation(first_upper, day_stem), stem_lodging),
        Lesson("二课", first_upper, second_upper, relation(second_upper, first_upper), first_upper),
        Lesson("三课", day_branch, third_upper, relation(third_upper, day_branch), day_branch),
        Lesson("四课", third_upper, fourth_upper, relation(fourth_upper, third_upper), third_upper),
    )


def build_heavenly_generals(calendar: CalendarInfo, heaven_plate: dict[str, str]) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, str]]]:
    day_stem = calendar.day_gz[0]
    day_noble, night_noble = DAY_NOBLEMAN[day_stem]
    is_day = calendar.hour_branch in "卯辰巳午未申"
    noble_branch = day_noble if is_day else night_noble
    noble_earth = next(earth for earth, heaven in heaven_plate.items() if heaven == noble_branch)
    if noble_earth in "亥子丑寅卯辰":
        heaven_order = rotate_from(noble_branch)
        direction = "顺布"
    else:
        start = BRANCHES.index(noble_branch)
        heaven_order = [BRANCHES[(start - offset) % len(BRANCHES)] for offset in range(len(BRANCHES))]
        direction = "逆布"
    heaven_generals = dict(zip(heaven_order, HEAVENLY_GENERALS, strict=True))
    generals = {
        earth: heaven_generals[heaven]
        for earth, heaven in heaven_plate.items()
    }
    officers = {
        branch: {
            "branch": branch,
            "heaven": heaven_plate[branch],
            "short": short,
            "name": HEAVENLY_OFFICER_NAMES[short],
        }
        for branch, short in generals.items()
    }
    return {
        "day_noble": day_noble,
        "night_noble": night_noble,
        "used": noble_branch,
        "mode": "day" if is_day else "night",
        "mounted_earth": noble_earth,
        "direction": direction,
    }, generals, officers


def build_six_relatives(calendar: CalendarInfo, heaven_plate: dict[str, str]) -> dict[str, dict[str, str]]:
    day_element = STEM_ELEMENTS[calendar.day_gz[0]]
    return {
        earth: {
            "branch": earth,
            "heaven": heaven,
            "relative": _six_relative(day_element, BRANCH_ELEMENTS[heaven]),
        }
        for earth, heaven in heaven_plate.items()
    }


def _six_relative(day_element: str, other_element: str) -> str:
    if other_element == day_element:
        return "兄弟"
    if GENERATING[other_element] == day_element:
        return "父母"
    if GENERATING[day_element] == other_element:
        return "子孙"
    if CONTROLLING[day_element] == other_element:
        return "妻财"
    if CONTROLLING[other_element] == day_element:
        return "官鬼"
    raise ValueError(f"cannot derive six relative for {day_element=} {other_element=}")


def build_transmission_details(
    transmissions: Transmissions,
    heaven_plate: dict[str, str],
    heavenly_generals: dict[str, str],
    heavenly_officers: dict[str, dict[str, str]],
    six_relatives: dict[str, dict[str, str]],
    xun_dun: dict,
    month_branch: str,
) -> tuple[dict[str, str | None], dict[str, str | None], dict[str, str | None]]:
    details = []
    for branch in transmissions.items:
        if branch is None:
            details.append({
                "branch": None,
                "earth": None,
                "general": None,
                "officer": None,
                "relative": None,
                "dun_gan": None,
                "season_state": None,
            })
            continue
        earth = next(earth for earth, heaven in heaven_plate.items() if heaven == branch)
        details.append({
            "branch": branch,
            "earth": earth,
            "general": heavenly_generals[earth],
            "officer": heavenly_officers[earth]["name"],
            "relative": six_relatives[earth]["relative"],
            "dun_gan": xun_dun["branch_to_stem"][branch],
            "season_state": season_state(branch, month_branch),
        })
    return tuple(details)  # type: ignore[return-value]


def build_lesson_bodies(transmissions: Transmissions) -> tuple[dict[str, str], ...]:
    return ({
        "name": f"{transmissions.method}课",
        "category": "九宗门",
        "evidence": transmissions.note,
    },)


def build_brief_analysis(transmissions: Transmissions, lesson_bodies: tuple[dict[str, str], ...]) -> str:
    body_names = " ".join(item["name"] for item in lesson_bodies)
    return f"课体：{body_names}; {transmissions.note}"


def build_chart_from_calendar(calendar: CalendarInfo, extra_spirit_positions: tuple[dict[str, str], ...] = ()) -> DaliurenChart:
    heaven_plate = build_heaven_plate(calendar.month_general, calendar.hour_branch)
    lessons = build_four_lessons(calendar, heaven_plate)
    transmissions = build_transmissions(lessons, heaven_plate)
    nobleman, generals, officers = build_heavenly_generals(calendar, heaven_plate)
    six_relatives = build_six_relatives(calendar, heaven_plate)
    xun_dun = build_xun_dun(calendar.day_gz)
    spirit_sha = build_spirit_sha(calendar, lessons, transmissions, extra_spirit_positions, xun_dun)
    transmission_details = build_transmission_details(transmissions, heaven_plate, generals, officers, six_relatives, xun_dun, calendar.month_gz[1])
    lesson_bodies = build_lesson_bodies(transmissions)
    brief_analysis = build_brief_analysis(transmissions, lesson_bodies)
    uncertainty = (
        "月将 V1 已按中气换将；历史案例若采用节气换将需显式切换规则。",
        "三传 V1 已覆盖九宗门主分支；涉害已按归本深浅初步评分，返吟无克驿马等细则仍需继续精校。",
        "贵人顺逆 V1 先按昼夜贵人顺布，后续需按派别规则校正。",
    )
    return DaliurenChart(
        calendar=calendar,
        month_general=calendar.month_general,
        heaven_plate=heaven_plate,
        earth_plate=tuple(BRANCHES),
        four_lessons=lessons,
        transmissions=transmissions,
        transmission_details=transmission_details,
        xun_dun=xun_dun,
        lesson_bodies=lesson_bodies,
        brief_analysis=brief_analysis,
        nobleman=nobleman,
        heavenly_generals=generals,
        heavenly_officers=officers,
        six_relatives=six_relatives,
        spirit_sha=spirit_sha,
        xunkong=calendar.xunkong,
        uncertainty=uncertainty,
    )


def build_chart(value, timezone: str = "Asia/Shanghai") -> DaliurenChart:
    calendar = get_calendar_info(value, timezone)
    return build_chart_from_calendar(calendar)
