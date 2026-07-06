"""Sports odds planning helpers for divination-backed match picks."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from operator import mul
from typing import Literal


Confidence = Literal["strong", "playable", "small", "avoid"]
RiskProfile = Literal["conservative", "balanced", "aggressive"]


@dataclass(frozen=True)
class MatchPick:
    match_id: str
    home: str
    away: str
    result_pick: str
    score_picks: tuple[str, ...] = ()
    half_full_pick: str | None = None
    confidence: Confidence = "playable"
    evidence_summary: str = ""


@dataclass(frozen=True)
class OddsQuote:
    match_id: str
    market: str
    selection: str
    decimal_odds: float
    source: str
    fetched_at: str


@dataclass(frozen=True)
class BetLeg:
    match_id: str
    market: str
    selection: str
    decimal_odds: float
    source: str
    fetched_at: str


@dataclass(frozen=True)
class BetPlan:
    kind: str
    legs: tuple[BetLeg, ...]
    combined_odds: float
    implied_probability: float
    stake_percent: float
    priority: int
    reason: str
    risk: str


@dataclass(frozen=True)
class RejectedPick:
    match_id: str
    market: str
    selection: str
    reason: str


@dataclass(frozen=True)
class BettingAnalysis:
    compact_lines: list[str]
    plans: list[BetPlan]
    rejected: list[RejectedPick]
    odds_table: list[dict[str, object]]


def implied_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("decimal_odds must be greater than 1")
    return 1 / decimal_odds


def combined_decimal_odds(decimal_odds: list[float] | tuple[float, ...]) -> float:
    if not decimal_odds:
        raise ValueError("at least one odds leg is required")
    for odds in decimal_odds:
        if odds <= 1:
            raise ValueError("all decimal odds must be greater than 1")
    return reduce(mul, decimal_odds, 1.0)


def stake_split(risk_profile: RiskProfile) -> dict[str, float]:
    splits: dict[str, dict[str, float]] = {
        "conservative": {"main": 80.0, "secondary": 15.0, "longshot": 5.0},
        "balanced": {"main": 65.0, "secondary": 25.0, "longshot": 10.0},
        "aggressive": {"main": 50.0, "secondary": 30.0, "longshot": 20.0},
    }
    try:
        return splits[risk_profile].copy()
    except KeyError as exc:
        raise ValueError(f"unknown risk_profile: {risk_profile}") from exc


def build_betting_analysis(
    picks: list[MatchPick] | tuple[MatchPick, ...],
    odds: list[OddsQuote] | tuple[OddsQuote, ...],
    *,
    risk_profile: RiskProfile = "balanced",
) -> BettingAnalysis:
    split = stake_split(risk_profile)
    odds_by_key = _index_odds(odds)
    compact_lines = _compact_match_lines(picks)
    compact_lines.append("推荐购买套路：胜负 | 比分 | 半全场")

    plans: list[BetPlan] = []
    rejected: list[RejectedPick] = []

    supported_result_legs: list[tuple[MatchPick, BetLeg]] = []
    for pick in picks:
        result_quote = odds_by_key.get((pick.match_id, "胜负", pick.result_pick))
        if pick.confidence == "avoid":
            rejected.append(
                RejectedPick(
                    pick.match_id,
                    "胜负",
                    pick.result_pick,
                    "confidence=avoid，不进入主推或串关",
                )
            )
            continue
        if result_quote is None:
            rejected.append(
                RejectedPick(pick.match_id, "胜负", pick.result_pick, "缺少胜负赔率")
            )
            continue
        if pick.confidence in {"strong", "playable"}:
            supported_result_legs.append((pick, _leg_from_quote(result_quote)))
        else:
            rejected.append(
                RejectedPick(
                    pick.match_id,
                    "胜负",
                    pick.result_pick,
                    "confidence=small，仅适合小注，不进入主推或串关",
                )
            )

    if supported_result_legs:
        best_pick, best_leg = _best_main_leg(supported_result_legs)
        plans.append(
            _plan(
                "主推单关",
                (best_leg,),
                split["main"],
                1,
                f"{best_pick.confidence} 胜负主象，{best_pick.evidence_summary}",
                "单关风险最低，但仍受临场阵容和赔率波动影响。",
            )
        )

    parlay_legs = tuple(leg for pick, leg in supported_result_legs)
    if len(parlay_legs) >= 2:
        plans.append(
            _plan(
                "串关方案",
                parlay_legs,
                split["secondary"],
                2,
                "仅串 strong/playable 胜负腿，避免把比分和半全场强行入主串。",
                "串关任一场失手即失效，方差高于单关。",
            )
        )

    for pick in picks:
        if pick.confidence not in {"strong", "playable", "small"}:
            continue
        score_plan = _first_available_score_plan(pick, odds_by_key, split["longshot"])
        if score_plan is not None:
            plans.append(score_plan)
        elif pick.score_picks:
            rejected.append(
                RejectedPick(
                    pick.match_id,
                    "比分",
                    "/".join(pick.score_picks),
                    "缺少匹配比分赔率",
                )
            )

        half_full_plan = _half_full_plan(pick, odds_by_key, split["longshot"])
        if half_full_plan is not None:
            plans.append(half_full_plan)
        elif pick.half_full_pick:
            rejected.append(
                RejectedPick(
                    pick.match_id,
                    "半全场",
                    pick.half_full_pick,
                    "非 strong 或缺少半全场赔率，不入主推",
                )
            )

    return BettingAnalysis(
        compact_lines=compact_lines,
        plans=plans,
        rejected=rejected,
        odds_table=[_odds_row(quote) for quote in odds],
    )


def _index_odds(
    odds: list[OddsQuote] | tuple[OddsQuote, ...],
) -> dict[tuple[str, str, str], OddsQuote]:
    return {(quote.match_id, quote.market, quote.selection): quote for quote in odds}


def _compact_match_lines(picks: list[MatchPick] | tuple[MatchPick, ...]) -> list[str]:
    lines = []
    for idx, pick in enumerate(picks, start=1):
        score = "/".join(pick.score_picks) if pick.score_picks else "比分不入主推"
        half_full = pick.half_full_pick or "半全场不入主推"
        lines.append(
            f"场次{idx}->{pick.home}VS{pick.away}: "
            f"{pick.result_pick} | {score} | {half_full}"
        )
    return lines


def _leg_from_quote(quote: OddsQuote) -> BetLeg:
    return BetLeg(
        match_id=quote.match_id,
        market=quote.market,
        selection=quote.selection,
        decimal_odds=quote.decimal_odds,
        source=quote.source,
        fetched_at=quote.fetched_at,
    )


def _best_main_leg(supported: list[tuple[MatchPick, BetLeg]]) -> tuple[MatchPick, BetLeg]:
    confidence_rank = {"strong": 0, "playable": 1, "small": 2, "avoid": 3}
    return sorted(
        supported,
        key=lambda item: (confidence_rank[item[0].confidence], item[1].decimal_odds),
    )[0]


def _plan(
    kind: str,
    legs: tuple[BetLeg, ...],
    stake_percent: float,
    priority: int,
    reason: str,
    risk: str,
) -> BetPlan:
    odds = combined_decimal_odds(tuple(leg.decimal_odds for leg in legs))
    return BetPlan(
        kind=kind,
        legs=legs,
        combined_odds=odds,
        implied_probability=implied_probability(odds),
        stake_percent=stake_percent,
        priority=priority,
        reason=reason,
        risk=risk,
    )


def _first_available_score_plan(
    pick: MatchPick,
    odds_by_key: dict[tuple[str, str, str], OddsQuote],
    stake_percent: float,
) -> BetPlan | None:
    for score in pick.score_picks:
        quote = odds_by_key.get((pick.match_id, "比分", score))
        if quote is None:
            continue
        return _plan(
            "比分小注",
            (_leg_from_quote(quote),),
            stake_percent,
            3,
            f"比分只取窄区间第一可用赔率：{score}",
            "精确比分方差很高，只适合小注或放弃。",
        )
    return None


def _half_full_plan(
    pick: MatchPick,
    odds_by_key: dict[tuple[str, str, str], OddsQuote],
    stake_percent: float,
) -> BetPlan | None:
    if not pick.half_full_pick or pick.confidence != "strong":
        return None
    quote = odds_by_key.get((pick.match_id, "半全场", pick.half_full_pick))
    if quote is None:
        return None
    return _plan(
        "半全场",
        (_leg_from_quote(quote),),
        stake_percent,
        4,
        "仅 strong 且早晚走势明确时纳入半全场。",
        "半全场依赖进球顺序，波动高于胜负。",
    )


def _odds_row(quote: OddsQuote) -> dict[str, object]:
    return {
        "match_id": quote.match_id,
        "market": quote.market,
        "selection": quote.selection,
        "decimal_odds": quote.decimal_odds,
        "implied_probability": implied_probability(quote.decimal_odds),
        "source": quote.source,
        "fetched_at": quote.fetched_at,
    }
