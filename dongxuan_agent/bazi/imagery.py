from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.knowledge import relative_source, resolve_knowledge_location
from .discipline import build_discipline_profile, build_middle_image_scores, discipline_runtime_config
from .knowledge import load_bazi_symbolic_layers
from .rules import format_template, format_value, get_path, matches, number
from .spirits import build_bazi_spirit_sha_analysis


def build_imagery_analysis(payload: dict) -> dict:
    data, status, source = load_bazi_symbolic_layers()
    runtime = data.get("imagery_runtime") or {}
    policy = runtime.get("answer_policy") or {}
    question = payload.get("question") or ""
    domain = _question_domain(question, payload, runtime)
    context = _context_frame(payload, runtime)
    facts = {**payload, "question_domain": domain, "context_frame": context}
    candidates = _candidate_images(facts, runtime)
    candidates = sorted(candidates, key=lambda item: item["score"], reverse=True)
    main = candidates[0] if candidates else _empty_image()
    secondary = _secondary_image(candidates, main)
    return {
        "knowledge_runtime": {"source": source, "status": status},
        "question_domain": domain,
        "context_frame": context,
        "symbol_sources": _symbol_sources(payload),
        "candidate_images": candidates,
        "main_image": main,
        "secondary_image": secondary,
        "answer_guidance": _answer_guidance(payload, domain, main, secondary, data, runtime),
        "avoid_images": list(policy.get("avoid_images") or []),
        "reasoning_chain": _reasoning_chain(main, secondary, policy),
        "uncertainty": list(policy.get("uncertainty") or []),
    }


def _question_domain(question: str, payload: dict, runtime: dict) -> str | None:
    for rule in runtime.get("question_domains") or []:
        if any(keyword in question for keyword in rule.get("keywords") or []):
            return rule.get("name")
    fallback = runtime.get("fallback_domains") or {}
    return fallback.get("with_analysis_hints") if payload.get("analysis_hints") else fallback.get("default")


def _context_frame(payload: dict, runtime: dict) -> dict:
    calendar = payload["chart"]["calendar"] if "chart" in payload else payload["calendar"]
    birth_year = datetime.fromisoformat(calendar["datetime"]).year
    target_year = (payload.get("analysis_hints") or {}).get("target_year")
    virtual_age = target_year - birth_year + 1 if target_year else None
    stage = runtime.get("default_context_stage") or {}
    if virtual_age is not None:
        stage = next((
            item for item in runtime.get("context_stages") or []
            if number(item.get("min_virtual_age")) <= virtual_age <= number(item.get("max_virtual_age"))
        ), stage)
    age_stage = stage.get("name")
    modern_context = list(stage.get("modern_context") or [])
    evidence = []
    if virtual_age is not None:
        text = format_template(
            runtime.get("context_evidence_template", ""),
            {"virtual_age": virtual_age, "age_stage": age_stage},
        )
        evidence.append(_evidence(
            "analysis_hints.current_luck.virtual_age",
            virtual_age,
            "按目标年虚岁判断现代阶段",
            text,
        ))
    return {
        "age_stage": age_stage,
        "modern_context": modern_context,
        "evidence": evidence,
    }


def _candidate_images(facts: dict, runtime: dict) -> list[dict]:
    candidates = []
    for rule in runtime.get("candidate_rules") or []:
        if not matches(rule.get("when"), facts):
            continue
        score = number(rule.get("score"))
        for adjustment in rule.get("score_adjustments") or []:
            if matches(adjustment.get("when"), facts):
                score += number(adjustment.get("delta"))
        evidence = [_configured_evidence(item, facts) for item in rule.get("evidence") or []]
        candidates.append(_image(rule.get("domain"), rule.get("image"), score, evidence))

    for candidate in candidates:
        candidate_facts = {**facts, "candidate": candidate}
        for rule in runtime.get("context_bias_rules") or []:
            if not matches(rule.get("when"), candidate_facts):
                continue
            candidate["score"] += number(rule.get("delta"))
            candidate["evidence"].append(_configured_evidence(rule.get("evidence") or {}, candidate_facts))
    return [item for item in candidates if item["evidence"]]


def _configured_evidence(specification: dict, facts: dict) -> dict:
    source_field = specification.get("source_field", "")
    value_path = specification.get("source_value_path") or source_field
    value = get_path(facts, value_path)
    rendered_value = format_value(value, specification.get("value_format"))
    text = specification.get("text", "").replace("{value}", rendered_value)
    text = format_template(text, facts)
    return _evidence(source_field, value, specification.get("rule", ""), text)


def _symbol_sources(payload: dict) -> list[dict]:
    sources = []
    pattern = payload.get("pattern_analysis", {}).get("primary_pattern", {})
    if pattern:
        sources.append({"symbol": pattern.get("name"), "image": "格局取象来源", "evidence": [_evidence("pattern_analysis.primary_pattern", pattern, "格局", f"主格局候选为{pattern.get('name')}。")]})
    flow = (payload.get("analysis_hints") or {}).get("flow_year") or {}
    if flow:
        sources.append({"symbol": flow.get("stem_ten_god"), "image": "流年外显十神", "evidence": [_evidence("analysis_hints.flow_year", flow, "流年", f"流年为{flow.get('ganzhi')}，天干十神{flow.get('stem_ten_god')}。")]})
    return sources


def _secondary_image(candidates: list[dict], main: dict) -> dict:
    for item in candidates:
        if item is not main and item["domain"] != main.get("domain"):
            return item
    return candidates[1] if len(candidates) > 1 else _empty_image()


def _reasoning_chain(main: dict, secondary: dict, policy: dict) -> list[str]:
    chain = []
    if main.get("domain"):
        chain.append(f"主象收敛为{main['domain']}：{main['image']}")
    if secondary.get("domain"):
        chain.append(f"次象保留为{secondary['domain']}：{secondary['image']}")
    if policy.get("reasoning_evidence_rule"):
        chain.append(policy["reasoning_evidence_rule"])
    return chain


def _answer_guidance(
    payload: dict,
    domain: str | None,
    main: dict,
    secondary: dict,
    data: dict,
    runtime: dict,
) -> dict:
    policy = runtime.get("answer_policy") or {}
    if domain != policy.get("major_domain"):
        return {}
    question = payload.get("question") or ""
    spirit_sha = build_bazi_spirit_sha_analysis(payload)
    base_middle_scores = _base_middle_image_scores(payload, runtime)
    discipline_config = discipline_runtime_config(data)
    middle_image_scores = build_middle_image_scores(
        base_middle_scores,
        spirit_sha,
        question,
        config=discipline_config,
    )
    discipline_profile = build_discipline_profile(
        middle_image_scores,
        question,
        config=discipline_config,
    )
    query_terms = _knowledge_query_terms(payload, main, secondary, runtime)
    return {
        "major_or_career_identification": {
            "rule": policy.get("rule"),
            "max_real_world_landings": policy.get("max_real_world_landings"),
            "knowledge_query_terms": query_terms,
            "knowledge_sources": _knowledge_sources(query_terms),
            "symbolic_layers": _symbolic_layers(payload, data, runtime),
            "landing_evidence": _landing_evidence(payload, data, runtime),
            "symbolic_dynamics": _symbolic_dynamics(payload),
            "direction_profile": _direction_profile(payload, main, secondary, runtime),
            "spirit_sha_analysis": spirit_sha,
            "middle_image_scores": middle_image_scores,
            "discipline_profile": discipline_profile,
            "llm_landing_constraints": discipline_profile["constraints_for_llm"],
            "evidence": _season_strength_evidence(payload),
            "forbidden": policy.get("forbidden"),
        }
    }


def _knowledge_query_terms(payload: dict, main: dict, secondary: dict, runtime: dict) -> list[str]:
    terms = list(runtime.get("knowledge_query_base_terms") or [])
    chart = payload.get("chart") or payload
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    if pattern.get("name"):
        terms.append(pattern["name"])
    for pillar in chart.get("pillars", []):
        terms.append(pillar.get("name", ""))
        if pillar.get("name") == "日柱":
            terms.append("日支")
        stem_ten_god = pillar.get("stem_ten_god")
        if stem_ten_god and stem_ten_god != "日主":
            terms.append(stem_ten_god)
        for hidden in pillar.get("hidden_stems", []):
            ten_god = hidden.get("ten_god")
            if ten_god and ten_god != "日主":
                terms.append(ten_god)
    for relation in chart.get("branch_relationships", []):
        terms.append(f"{relation.get('branches', '')}{relation.get('type', '')}")
    strength = payload.get("strength_analysis") or {}
    forces = strength.get("element_forces") or {}
    for element, item in sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)[:3]:
        terms.append(element)
    if main.get("domain"):
        terms.append(main["domain"])
    if secondary.get("domain"):
        terms.append(secondary["domain"])
    return list(dict.fromkeys(terms))


def _knowledge_sources(terms: list[str]) -> list[dict]:
    location = resolve_knowledge_location()
    if location.status != "available":
        return []
    sources = []
    for term in terms:
        path = _knowledge_path(term, location.root)
        if not path:
            continue
        excerpt = _knowledge_excerpt(path, term)
        if not excerpt:
            continue
        sources.append({
            "term": term,
            "source": relative_source(path, location.root),
            "excerpt": excerpt,
        })
        if len(sources) >= 6:
            break
    return sources


def _knowledge_path(term: str, root: Path) -> Path | None:
    if not term or "/" in term or "\\" in term or term in {".", ".."}:
        return None
    candidates = [
        root / "entities" / f"{term}.md",
        root / "topics" / f"{term}.md",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _knowledge_excerpt(path: Path, term: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content = []
    for line in lines:
        if line.startswith("---") or line.startswith("tags:") or line.startswith("created:") or line.startswith("updated:") or line.startswith("sources:"):
            continue
        content.append(line)
        if len(content) >= 5:
            break
    excerpt = " ".join(content)
    return excerpt[:240] or term


def _symbolic_layers(payload: dict, data: dict, runtime: dict) -> dict:
    _, status, source = load_bazi_symbolic_layers()
    query_terms = set(_knowledge_query_terms(payload, {}, {}, runtime))
    active_middle = _active_middle_image_names(payload, runtime)
    return {
        "source": source,
        "availability": {"status": status},
        "traditional_symbols": [
            item for item in data.get("traditional_symbols", [])
            if item.get("name") in query_terms or item.get("kind") in query_terms
        ],
        "middle_images": [
            item for item in data.get("middle_images", [])
            if item.get("name") in active_middle
        ],
        "modern_landing_rules": [
            item for item in data.get("modern_landing_rules", [])
            if set(item.get("requires_all", [])).issubset(active_middle)
        ],
    }


def _landing_evidence(payload: dict, data: dict, runtime: dict) -> dict:
    active_middle = _active_middle_image_names(payload, runtime)
    middle_strengths = _middle_image_strengths(payload, active_middle, runtime)
    result: dict[str, list[dict[str, object]]] = {"supported": [], "weakened": [], "excluded": []}
    for rule in data.get("modern_landing_rules", []):
        required = set(rule.get("requires_all", []))
        prefers = set(rule.get("prefers_any", []))
        missing = sorted(required - active_middle)
        preferred_hits = sorted(prefers & active_middle)
        evidence = []
        if required:
            evidence.append(f"必要画像：{ '、'.join(rule.get('requires_all', [])) }。")
        if required - set(missing):
            evidence.append(f"已成立画像：{ '、'.join(sorted(required & active_middle)) }。")
        if preferred_hits:
            evidence.append(f"加强画像：{ '、'.join(preferred_hits) }。")
        evidence.extend(_landing_strength_evidence(rule, middle_strengths, active_middle))
        weak_reasons = _landing_rule_weak_reasons(rule, middle_strengths, runtime)
        if missing:
            evidence.append(f"缺少必要画像：{ '、'.join(missing) }。")
            status = "excluded"
        elif weak_reasons:
            status = "weakened"
            evidence.extend(weak_reasons)
        else:
            status = "supported"
        result[status].append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
            "explanation": rule.get("explanation"),
        })
    return result


def _landing_strength_evidence(rule: dict, middle_strengths: dict[str, dict], active_middle: set[str]) -> list[str]:
    names = list(dict.fromkeys([*rule.get("requires_all", []), *rule.get("prefers_any", [])]))
    evidence = []
    for name in names:
        if name not in active_middle:
            continue
        item = middle_strengths.get(name, {"score": 0, "reasons": []})
        reason_text = "；".join(item.get("reasons", [])) or "由命盘字段合参成立"
        evidence.append(f"{name}画像强弱：{item.get('score')}。{reason_text}。")
    return evidence


def _landing_rule_weak_reasons(rule: dict, middle_strengths: dict[str, dict], runtime: dict) -> list[str]:
    reasons = []
    minimum = number(runtime.get("landing_required_min_score"))
    for name in rule.get("requires_all", []):
        item = middle_strengths.get(name, {"score": 0, "reasons": []})
        if number(item.get("score")) < minimum:
            reasons.append(f"{rule['name']}降级：必要画像{name}强度不足，不能作为第一落点。")
    facts = {"middle_scores": middle_strengths}
    for condition in rule.get("weakening_conditions") or []:
        if matches(condition.get("when"), facts):
            reasons.append(f"{rule['name']}降级：{condition.get('reason')}。")
    return reasons


def _middle_image_strengths(payload: dict, active_middle: set[str], runtime: dict) -> dict[str, dict]:
    scoring = runtime.get("middle_image_scoring") or {}
    initial_score = number(scoring.get("initial_score"))
    context = _context_frame(payload, runtime)
    facts = {**payload, "context_frame": context}
    strengths: dict[str, dict[str, Any]] = {
        name: {"score": initial_score, "reasons": []}
        for name in active_middle
    }
    for rule in scoring.get("rules") or []:
        name = rule.get("image")
        if name not in strengths:
            continue
        delta = number(rule.get("delta")) if matches(rule.get("when"), facts) else number(rule.get("else_delta"))
        strengths[name]["score"] = round(strengths[name]["score"] + delta, 2)
        if rule.get("reason"):
            strengths[name]["reasons"].append(format_template(rule["reason"], facts))
    default_reason = scoring.get("default_reason")
    for item in strengths.values():
        if not item["reasons"] and default_reason:
            item["reasons"].append(default_reason)
    return strengths


def _base_middle_image_scores(payload: dict, runtime: dict) -> dict[str, dict]:
    active_middle = _active_middle_image_names(payload, runtime)
    strengths = _middle_image_strengths(payload, active_middle, runtime)
    return {
        name: {
            "score": item.get("score", 0),
            "evidence": item.get("reasons", []),
        }
        for name, item in strengths.items()
    }


def _active_middle_image_names(payload: dict, runtime: dict) -> set[str]:
    context = _context_frame(payload, runtime)
    facts = {**payload, "context_frame": context}
    return {
        rule["name"]
        for rule in runtime.get("active_middle_image_rules") or []
        if rule.get("name") and matches(rule.get("when"), facts)
    }


def _symbolic_dynamics(payload: dict) -> dict:
    forces = (payload.get("strength_analysis") or {}).get("element_forces") or {}
    climate = payload.get("climate_analysis") or {}
    pattern = (payload.get("pattern_analysis") or {}).get("primary_pattern") or {}
    remedy = payload.get("remedy_analysis") or {}
    hints = payload.get("analysis_hints") or {}
    relations = hints.get("activated_relations") or []

    sorted_forces = sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)
    dominant = [
        f"{element}有效力{item.get('effective_power')}、季节系数{item.get('season_power')}、{item.get('root_status')}"
        for element, item in sorted_forces[:2]
    ]
    usable = [
        f"{item.get('element')}为{item.get('role')}"
        for item in remedy.get("remedy_candidates", [])
        if item.get("element") and item.get("role")
    ]
    weakened = [
        f"{element}有效力{item.get('effective_power')}、季节系数{item.get('season_power')}、{item.get('root_status')}"
        for element, item in sorted_forces
        if item.get("effective_power", 0) <= 0.8 or item.get("root_status") in {"无根", "根受损"}
    ]
    relation_text = [item.get("evidence") for item in relations if item.get("evidence")]
    if pattern.get("name"):
        relation_text.append(f"月令取格为{pattern['name']}，证据为{pattern.get('evidence')}")
    if climate.get("season_profile"):
        relation_text.append(f"调候背景为{climate.get('season_profile')}，寒暖燥湿为{climate.get('temperature')}/{climate.get('moisture')}")

    return {
        "dominant": dominant,
        "usable": usable,
        "weakened": weakened,
        "relations": relation_text,
    }


def _direction_profile(payload: dict, main: dict, secondary: dict, runtime: dict) -> dict:
    policy = runtime.get("direction_profile") or {}
    context = _context_frame(payload, runtime)
    facts = {
        **payload,
        "context_frame": context,
        "main_image": main,
        "secondary_image": secondary,
    }
    favorable = [
        format_template(value, facts)
        for rule in policy.get("favorable_rules") or []
        if matches(rule.get("when"), facts)
        for value in rule.get("values") or []
    ]
    weak = [
        format_template(value, facts)
        for rule in policy.get("weak_rules") or []
        if matches(rule.get("when"), facts)
        for value in rule.get("values") or []
    ]
    for source in policy.get("weak_value_sources") or []:
        values = get_path(facts, source.get("path", ""), []) or []
        weak.extend(str(value) for value in values[: int(number(source.get("limit")))])

    constraints = list(policy.get("constraints") or [])
    if main.get("domain"):
        constraints.append(format_template(policy.get("main_constraint_template", ""), facts))
    if secondary.get("domain"):
        constraints.append(format_template(policy.get("secondary_constraint_template", ""), facts))

    return {
        "favorable_modes": list(dict.fromkeys(favorable)),
        "weak_or_unsuitable_modes": list(dict.fromkeys(weak)),
        "real_world_landing_constraints": constraints,
    }


def _season_strength_evidence(payload: dict) -> list[dict]:
    strength = payload.get("strength_analysis") or {}
    month_branch = strength.get("month_branch")
    forces = strength.get("element_forces") or {}
    evidence = []
    for element, item in sorted(forces.items(), key=lambda pair: pair[1].get("effective_power", 0), reverse=True)[:3]:
        evidence.append(_evidence(
            f"strength_analysis.element_forces.{element}",
            {
                "season_power": item.get("season_power"),
                "effective_power": item.get("effective_power"),
                "root_status": item.get("root_status"),
            },
            "月令季节力量与有效力量",
            f"{month_branch}月下{element}的季节系数为{item.get('season_power')}，有效力量为{item.get('effective_power')}，根气状态为{item.get('root_status')}。",
        ))
    day_strength = strength.get("day_master_strength") or {}
    for text in day_strength.get("evidence", [])[:2]:
        evidence.append(_evidence("strength_analysis.day_master_strength.evidence", text, "日主强弱证据", text))
    return evidence


def _image(domain: str, image: str, score: int, evidence: list[dict]) -> dict:
    return {
        "domain": domain,
        "image": image,
        "score": score,
        "evidence": evidence,
    }


def _empty_image() -> dict:
    return {"domain": None, "image": None, "score": 0, "evidence": []}


def _evidence(source_field: str, source_value, rule: str, text: str) -> dict:
    return {
        "source_field": source_field,
        "source_value": source_value,
        "rule": rule,
        "text": text,
    }
