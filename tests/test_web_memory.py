import json


def test_case_store_creates_bazi_case_with_expected_memory_fields(tmp_path):
    from dongxuan_agent.web.memory import CaseStore

    store = CaseStore(tmp_path / "memory.json")
    case = store.create_case(
        {
            "title": "案例一",
            "system": "bazi",
            "birth": {
                "datetime": "2006-12-18 12:30:00",
                "timezone": "Asia/Shanghai",
                "region": "",
                "gender": "男",
                "longitude": None,
                "zi_hour_rule": "whole",
            },
            "bazi": {"year": "丙戌", "month": "庚子", "day": "辛卯", "hour": "甲午"},
            "luck": {"start_age": None, "pillars": []},
            "background": "目前关注财运",
            "facts": [{"text": "2025年财务压力已验证"}],
            "intents": [{"text": "验证2026年是否转好"}],
        }
    )

    assert case["id"].startswith("case_")
    assert case["system"] == "bazi"
    assert case["birth"]["region"] == ""
    assert case["facts"][0]["confidence"] == "verified"
    assert case["intents"][0]["status"] == "pending"

    saved = json.loads((tmp_path / "memory.json").read_text(encoding="utf-8"))
    assert saved["version"] == 1
    assert saved["cases"][0]["id"] == case["id"]


def test_case_store_updates_background_facts_intents_and_summary(tmp_path):
    from dongxuan_agent.web.memory import CaseStore

    store = CaseStore(tmp_path / "memory.json")
    case = store.create_case({"title": "案例一", "system": "bazi"})

    updated = store.update_case(
        case["id"],
        {
            "background": "短线交易背景",
            "facts": [{"text": "五月先赚后回撤", "source": "user_verified"}],
            "intents": [{"text": "验证六月是否继续亏损"}],
            "notes": {"summary": "围绕财务波动追问。"},
        },
    )

    assert updated["background"] == "短线交易背景"
    assert updated["facts"][0]["source"] == "user_verified"
    assert updated["facts"][0]["confidence"] == "verified"
    assert updated["intents"][0]["status"] == "pending"
    assert updated["notes"]["summary"] == "围绕财务波动追问。"


def test_case_store_appends_analysis_record_without_unbounded_history(tmp_path):
    from dongxuan_agent.web.memory import CaseStore

    store = CaseStore(tmp_path / "memory.json", max_records=2)
    case = store.create_case({"title": "案例一", "system": "bazi"})

    store.append_record(case["id"], question="第一问", analysis="A1", conclusion="C1", context={"a": 1})
    store.append_record(case["id"], question="第二问", analysis="A2", conclusion="C2", context={"a": 2})
    updated = store.append_record(case["id"], question="第三问", analysis="A3", conclusion="C3", context={"a": 3})

    assert [record["question"] for record in updated["records"]] == ["第二问", "第三问"]
    assert updated["records"][-1]["conclusion"] == "C3"


def test_case_store_merges_bazi_luck_and_year_snapshot(tmp_path):
    from dongxuan_agent.web.memory import CaseStore

    store = CaseStore(tmp_path / "memory.json")
    case = store.create_case({"title": "案例一", "system": "bazi"})

    updated = store.merge_chart_snapshot(
        case["id"],
        {
            "calendar": {"datetime": "2006-11-05T06:00:00+08:00"},
            "day_master": {"stem": "戊"},
            "pillars": [{"name": "年柱", "ganzhi": "丙戌"}],
            "luck": {"cycles": [{"ganzhi": "壬寅"}]},
            "analysis_hints": {"target_year": 2026, "year_ganzhi": "丙午"},
            "luck_year_remedy": {"combined_effect": "药病并见"},
        },
    )

    assert updated["bazi"]["pillars"][0]["ganzhi"] == "丙戌"
    assert updated["luck"]["cycles"][0]["ganzhi"] == "壬寅"
    assert updated["notes"]["year_hints"]["2026"]["year_ganzhi"] == "丙午"
    assert updated["notes"]["luck_year_remedy"]["2026"]["combined_effect"] == "药病并见"
