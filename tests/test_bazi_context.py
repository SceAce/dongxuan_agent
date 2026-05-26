from dongxuan_agent.bazi.context import build_bazi_context


def test_bazi_context_builds_full_payload_with_stable_fields():
    payload = build_bazi_context(
        "2006-12-18 12:30:00",
        timezone="Asia/Shanghai",
        gender="男",
        target_year=2025,
        question="推断2025年发生了什么",
    )

    assert payload["calendar"]["year_gz"] == "丙戌"
    assert payload["strength_analysis"]["day_master_strength"]["day_master"] == "辛"
    assert payload["climate_analysis"]["season_profile"] == "子月寒水当令"
    assert payload["pattern_analysis"]["primary_pattern"]["name"] == "食神格"
    assert payload["remedy_analysis"]["priority"] == "调候优先"
    assert payload["god_candidates"]["candidate_gods"][0]["element"] == "火"
    assert payload["analysis_hints"]["year_ganzhi"] == "乙巳"
    assert payload["luck_year_remedy"]["combined_effect"] == "药病并见"
    assert payload["imagery_analysis"]["main_image"]["evidence"]
    assert payload["rule_cards"]["mode"] == "year_event"
