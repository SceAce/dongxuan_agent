import json
from inspect import signature

from dongxuan_agent.bazi.context import build_bazi_context


def test_bazi_context_builds_full_payload_with_stable_fields(available_knowledge_root):
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
    assert payload["knowledge_layers"]["layer_priority"] == ["理法", "象法", "案例"]
    assert payload["knowledge_layers"]["book_sets"]["principle"]
    assert payload["knowledge_layers"]["book_sets"]["symbolic"]
    assert payload["knowledge_layers"]["book_sets"]["cases"]
    assert payload["knowledge_layers"]["case_policy"]["prefer"] == "禄命派"
    assert payload["knowledge_layers"]["availability"]["status"] == "available"
    assert all(not page["source"].startswith("/") for page in payload["knowledge_layers"]["topic_pages"])
    assert "/home/source" not in json.dumps(payload["knowledge_layers"], ensure_ascii=False)


def test_bazi_context_does_not_expose_legacy_zi_hour_selector():
    assert "zi_hour_rule" not in signature(build_bazi_context).parameters


def test_malformed_symbolic_layers_degrades_without_absolute_path(monkeypatch, tmp_path):
    root = tmp_path / "wiki"
    structured = root / "structured"
    structured.mkdir(parents=True)
    (structured / "bazi_symbolic_layers.json").write_text("{broken", encoding="utf-8")
    monkeypatch.setenv("DONGXUAN_KNOWLEDGE_ROOT", str(root))

    context = build_bazi_context("2006-12-18 12:30:00")
    serialized = json.dumps(context, ensure_ascii=False)

    assert context["knowledge_layers"]["availability"]["status"] == "invalid"
    assert str(tmp_path) not in serialized
