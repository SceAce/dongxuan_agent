from __future__ import annotations

from dataclasses import dataclass

from .calendar_engine import get_calendar_info, with_hour_branch
from .chart import DaliurenChart, build_chart_from_calendar
from .constants import BRANCHES, JIAZI


@dataclass(frozen=True)
class DaliurenDivination:
    chart: DaliurenChart
    divination: dict[str, str | int | None]
    querent: dict[str, str | int | None]

    def to_dict(self) -> dict:
        payload = self.chart.to_dict()
        payload["divination"] = self.divination
        payload["querent"] = self.querent
        return payload


def number_to_hour_branch(number: int) -> str:
    if number <= 0:
        raise ValueError("报数必须为正整数")
    return BRANCHES[(number - 1) % 12]


def calculate_querent(
    *,
    gender: str,
    question: str,
    chart_year: int,
    background: str | None = None,
    birth_year: int | None = None,
) -> dict[str, str | int | None]:
    errors = []
    if gender not in {"男", "女"}:
        errors.append("性别必须为男或女")
    if not question.strip():
        errors.append("所问事不能为空")
    if errors:
        raise ValueError("；".join(errors))

    result: dict[str, str | int | None] = {
        "gender": gender,
        "question": question,
        "background": background,
        "birth_year": birth_year,
        "birth_year_ganzhi": None,
        "life_branch": None,
        "virtual_age": None,
        "traveling_year": None,
        "rule": "命取出生年地支；行年男从寅顺行、女从申逆行，按虚岁计。",
    }
    if birth_year is None:
        return result

    birth_gz = year_ganzhi(birth_year)
    virtual_age = chart_year - birth_year + 1
    if virtual_age <= 0:
        raise ValueError("出生年不能晚于起课年份")
    result["birth_year_ganzhi"] = birth_gz
    result["life_branch"] = birth_gz[1]
    result["virtual_age"] = virtual_age
    result["traveling_year"] = traveling_year(gender, virtual_age)
    return result


def year_ganzhi(year: int) -> str:
    return JIAZI[(year - 1984) % 60]


def traveling_year(gender: str, virtual_age: int) -> str:
    if virtual_age <= 0:
        raise ValueError("虚岁必须为正数")
    if gender == "男":
        start = BRANCHES.index("寅")
        return BRANCHES[(start + virtual_age - 1) % 12]
    if gender == "女":
        start = BRANCHES.index("申")
        return BRANCHES[(start - (virtual_age - 1)) % 12]
    raise ValueError("性别必须为男或女")


def build_divination(
    value,
    *,
    timezone: str = "Asia/Shanghai",
    mode: str = "time",
    hour_branch: str | None = None,
    number: int | None = None,
    gender: str,
    question: str,
    background: str | None = None,
    birth_year: int | None = None,
) -> DaliurenDivination:
    calendar = get_calendar_info(value, timezone)
    source_hour_branch: str
    if mode == "time":
        source_hour_branch = calendar.hour_branch
    elif mode == "live-hour":
        if hour_branch is None:
            raise ValueError("活时起课必须提供 hour_branch")
        source_hour_branch = _normalize_hour_branch(hour_branch)
        calendar = with_hour_branch(calendar, source_hour_branch)
    elif mode == "number":
        if number is None:
            raise ValueError("报数起课必须提供 number")
        source_hour_branch = number_to_hour_branch(number)
        calendar = with_hour_branch(calendar, source_hour_branch)
    else:
        raise ValueError("mode 必须为 time、live-hour 或 number")

    querent = calculate_querent(
        gender=gender,
        question=question,
        background=background,
        chart_year=calendar.dt.year,
        birth_year=birth_year,
    )
    chart = build_chart_from_calendar(calendar, extra_spirit_positions=_querent_spirit_positions(querent))
    divination = {
        "mode": mode,
        "number": number,
        "source_hour_branch": source_hour_branch,
        "rule": _mode_rule(mode),
    }
    return DaliurenDivination(chart=chart, divination=divination, querent=querent)


def _normalize_hour_branch(hour_branch: str) -> str:
    value = hour_branch.strip()
    if value not in BRANCHES:
        raise ValueError("hour_branch 必须为十二地支之一")
    return value


def _mode_rule(mode: str) -> str:
    if mode == "time":
        return "正时起课：以起课时间之时辰排盘。"
    if mode == "live-hour":
        return "活时起课：不换日、不换月将，只以所报/所抽地支替换时辰。"
    if mode == "number":
        return "报数起课：子1、丑2至亥12，超过12取余，余0作亥；不换日、不换月将，只换时辰。"
    raise ValueError(mode)


def _querent_spirit_positions(querent: dict[str, str | int | None]) -> tuple[dict[str, str], ...]:
    positions = []
    if querent.get("life_branch"):
        positions.append({"location": "本命", "branch": str(querent["life_branch"])})
    if querent.get("traveling_year"):
        positions.append({"location": "行年", "branch": str(querent["traveling_year"])})
    return tuple(positions)
