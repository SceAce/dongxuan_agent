from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from ..calendar_engine import CalendarInfo, get_calendar_info
from .hexagrams import (
    Hexagram,
    LineState,
    changed_binary,
    hexagram_by_binary,
    line_states_from_hexagrams,
    parse_line_states,
    parse_named_hexagram,
)
from .judgment import enrich_payload
from .najia import build_najia, palace_info
from .question import classify_question


RANDOM_STATES = ("老阴", "少阳", "少阴", "老阳")
RANDOM_WEIGHTS = (1, 3, 3, 1)


@dataclass(frozen=True)
class LiuyaoChart:
    method: str
    raw: str
    question: str | None
    calendar: CalendarInfo
    original: Hexagram
    changed: Hexagram
    lines: list[LineState]

    def to_dict(self) -> dict:
        moving_lines = [line.position for line in self.lines if line.moving]
        palace = palace_info(self.original)
        payload = {
            "schema": "liuyao_chart_v5",
            "input": {
                "method": self.method,
                "raw": self.raw,
                "line_order": "bottom_to_top",
                "question": self.question,
            },
            "calendar": _calendar_payload(self.calendar),
            "hexagram": {
                "original": _hexagram_payload(self.original),
                "changed": _hexagram_payload(self.changed),
                "moving_lines": moving_lines,
                "description": _hexagram_description(self.original, self.changed, moving_lines),
            },
            "lines": [_line_payload(line) for line in self.lines],
            "palace": palace,
            "najia": build_najia(self.original),
            "question_context": classify_question(self.question),
            "analysis_hints": _analysis_hints(moving_lines, self.lines, palace),
            "uncertainty": [
                "六爻 MVP 只生成排盘结构和候选检查项，不做最终吉凶、应期或用神定夺。",
            ],
        }
        return enrich_payload(payload)


def build_liuyao_chart(
    *,
    lines: str | None = None,
    hexagram: str | None = None,
    random_lines: bool = False,
    seed: int | None = None,
    question: str | None = None,
    value: str | datetime | None = None,
    timezone: str = "Asia/Shanghai",
) -> LiuyaoChart:
    provided = sum(item is not None for item in (lines, hexagram)) + int(random_lines)
    if provided != 1:
        raise ValueError("必须且只能提供一种起卦方式：--lines、--hexagram 或 --random。")
    calendar = get_calendar_info(value or datetime.now(), timezone)
    if lines is not None:
        parsed_lines = parse_line_states(lines)
        original = hexagram_by_binary("".join(line.yin_yang_binary for line in parsed_lines))
        changed = hexagram_by_binary(changed_binary(parsed_lines))
        return LiuyaoChart("manual_lines", lines, question, calendar, original, changed, parsed_lines)
    if hexagram is not None:
        parsed = parse_named_hexagram(hexagram)
        parsed_lines = line_states_from_hexagrams(parsed.original, parsed.moving_lines)
        return LiuyaoChart("named_hexagram", hexagram, question, calendar, parsed.original, parsed.changed, parsed_lines)
    generated = _random_line_states(seed)
    parsed_lines = parse_line_states(" ".join(generated))
    original = hexagram_by_binary("".join(line.yin_yang_binary for line in parsed_lines))
    changed = hexagram_by_binary(changed_binary(parsed_lines))
    return LiuyaoChart("random_lines", " ".join(generated), question, calendar, original, changed, parsed_lines)


def _random_line_states(seed: int | None) -> list[str]:
    rng = random.Random(seed)
    return rng.choices(RANDOM_STATES, weights=RANDOM_WEIGHTS, k=6)


def _calendar_payload(calendar: CalendarInfo) -> dict:
    return {
        "datetime": calendar.dt.isoformat(),
        "timezone": calendar.timezone,
        "year_gz": calendar.year_gz,
        "month_gz": calendar.month_gz,
        "day_gz": calendar.day_gz,
        "hour_gz": calendar.hour_gz,
        "month_branch": calendar.month_gz[1],
        "day_branch": calendar.day_gz[1],
        "xunkong": list(calendar.xunkong),
    }


def _hexagram_payload(hexagram: Hexagram) -> dict:
    return {
        "name": hexagram.name,
        "upper_trigram": hexagram.upper_trigram,
        "lower_trigram": hexagram.lower_trigram,
        "binary_bottom_to_top": hexagram.binary_bottom_to_top,
    }


def _line_payload(line: LineState) -> dict:
    return {
        "position": line.position,
        "name": line.name,
        "input_state": line.input_state,
        "yin_yang": line.yin_yang,
        "moving": line.moving,
        "changed_yin_yang": line.changed_yin_yang,
    }


def _hexagram_description(original: Hexagram, changed: Hexagram, moving_lines: list[int]) -> str:
    if not moving_lines:
        return f"{original.name}静卦"
    positions = "、".join(_line_name(position) for position in moving_lines)
    return f"{original.name}{positions}动，变{changed.name}"


def _analysis_hints(moving_lines: list[int], lines: list[LineState], palace: dict) -> dict:
    moving_summary = "静卦，无动爻"
    if moving_lines:
        moving_summary = "、".join(
            f"{line.name}动，{line.yin_yang}变{line.changed_yin_yang}" for line in lines if line.moving
        )
    return {
        "moving_summary": moving_summary,
        "shi_ying_summary": f"世在{palace['shi_line']}，应在{palace['ying_line']}",
        "useful_god_candidates": [],
        "must_check": [
            "月建日辰对用神、世爻、应爻的生克冲合",
            "动爻对世应和候选用神的作用",
            "变爻是否回头生克",
        ],
    }


def _line_name(position: int) -> str:
    return ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")[position - 1]
