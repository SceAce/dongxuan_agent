import pytest

from dongxuan_agent.sports_betting import (
    MatchPick,
    OddsQuote,
    build_betting_analysis,
    combined_decimal_odds,
    implied_probability,
    stake_split,
)


def test_implied_probability_from_decimal_odds():
    assert implied_probability(2.5) == pytest.approx(0.4)


def test_implied_probability_rejects_invalid_odds():
    with pytest.raises(ValueError, match="greater than 1"):
        implied_probability(1.0)


def test_combined_decimal_odds_multiplies_legs():
    assert combined_decimal_odds([1.8, 2.1, 1.5]) == pytest.approx(5.67)


def test_stake_split_uses_risk_profile_defaults():
    assert stake_split("conservative") == {
        "main": 80.0,
        "secondary": 15.0,
        "longshot": 5.0,
    }
    assert stake_split("balanced")["main"] == 65.0
    assert stake_split("aggressive")["longshot"] == 20.0


def test_build_betting_analysis_selects_supported_single_parlay_and_rejects_weak_legs():
    picks = [
        MatchPick(
            match_id="m1",
            home="Brazil",
            away="Japan",
            result_pick="Brazil win",
            score_picks=("2-0", "2-1"),
            half_full_pick="Brazil/Brazil",
            confidence="strong",
            evidence_summary="主客分象日强辰弱，末传归日方。",
        ),
        MatchPick(
            match_id="m2",
            home="France",
            away="Germany",
            result_pick="Draw",
            score_picks=("1-1",),
            half_full_pick=None,
            confidence="playable",
            evidence_summary="两方相持，末传不偏。",
        ),
        MatchPick(
            match_id="m3",
            home="Spain",
            away="Italy",
            result_pick="Spain win",
            score_picks=("1-0",),
            half_full_pick="Draw/Spain",
            confidence="avoid",
            evidence_summary="课象不显，不能同时测算多个比赛。",
        ),
    ]
    odds = [
        OddsQuote("m1", "胜负", "Brazil win", 1.72, "manual", "2026-06-28T22:00:00+08:00"),
        OddsQuote("m1", "比分", "2-0", 7.5, "manual", "2026-06-28T22:00:00+08:00"),
        OddsQuote("m1", "半全场", "Brazil/Brazil", 2.6, "manual", "2026-06-28T22:00:00+08:00"),
        OddsQuote("m2", "胜负", "Draw", 3.2, "manual", "2026-06-28T22:00:00+08:00"),
        OddsQuote("m2", "比分", "1-1", 6.2, "manual", "2026-06-28T22:00:00+08:00"),
        OddsQuote("m3", "胜负", "Spain win", 2.0, "manual", "2026-06-28T22:00:00+08:00"),
    ]

    analysis = build_betting_analysis(picks, odds, risk_profile="balanced")

    assert analysis.compact_lines[:3] == [
        "场次1->BrazilVSJapan: Brazil win | 2-0/2-1 | Brazil/Brazil",
        "场次2->FranceVSGermany: Draw | 1-1 | 半全场不入主推",
        "场次3->SpainVSItaly: Spain win | 1-0 | Draw/Spain",
    ]
    assert analysis.compact_lines[3] == "推荐购买套路：胜负 | 比分 | 半全场"

    plan_kinds = [plan.kind for plan in analysis.plans]
    assert "主推单关" in plan_kinds
    assert "串关方案" in plan_kinds
    assert "比分小注" in plan_kinds
    assert "半全场" in plan_kinds

    parlay = next(plan for plan in analysis.plans if plan.kind == "串关方案")
    assert [leg.match_id for leg in parlay.legs] == ["m1", "m2"]
    assert parlay.combined_odds == pytest.approx(5.504)

    rejected = {(item.match_id, item.reason) for item in analysis.rejected}
    assert ("m3", "confidence=avoid，不进入主推或串关") in rejected
