from __future__ import annotations

from typing import Any

from .knowledge import load_bazi_symbolic_layers
from .rules import format_template, number


def build_middle_image_scores(
    base_scores: dict[str, dict[str, Any]],
    spirit_sha_analysis: dict[str, Any],
    question: str = "",
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    runtime = _runtime_config() if config is None else config
    middle_images = set(runtime.get("middle_image_names") or [])
    scores: dict[str, dict[str, Any]] = {
        image: {
            "base_score": _base_score(item or {}),
            "spirit_delta": 0.0,
            "question_delta": 0.0,
            "final_score": 0.0,
            "evidence": list((item or {}).get("evidence") or []),
        }
        for image, item in base_scores.items()
        if image in middle_images
    }
    for image in middle_images:
        scores.setdefault(image, _empty_score())

    _apply_spirit_deltas(scores, spirit_sha_analysis, runtime)
    _apply_question_deltas(scores, question, runtime)
    return {
        image: {
            **item,
            "spirit_delta": round(item["spirit_delta"], 3),
            "question_delta": round(item["question_delta"], 3),
            "final_score": round(item["base_score"] + item["spirit_delta"] + item["question_delta"], 3),
        }
        for image, item in scores.items()
        if item["base_score"] or item["spirit_delta"] or item["question_delta"] or item["evidence"]
    }


def build_discipline_profile(
    middle_image_scores: dict[str, dict[str, Any]],
    question: str = "",
    *,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime = _runtime_config() if config is None else config
    groups = [
        _score_group(item.get("name", ""), item.get("weights") or {}, middle_image_scores, runtime)
        for item in runtime.get("groups") or []
    ]
    groups = [group for group in groups if group["score"] > 0]
    groups.sort(key=lambda item: (-item["score"], item["name"]))
    cross_domain = _is_cross_domain(groups, runtime.get("cross_domain") or {})
    return {
        "groups": groups,
        "cross_domain": cross_domain,
        "recommended_mode": _recommended_mode(groups, cross_domain, runtime),
        "constraints_for_llm": list(runtime.get("constraints_for_llm") or []),
    }


def discipline_runtime_config(data: dict[str, Any]) -> dict[str, Any]:
    runtime = dict(data.get("discipline_runtime") or {})
    runtime["middle_image_names"] = [
        item["name"]
        for item in data.get("middle_images") or []
        if isinstance(item, dict) and item.get("name")
    ]
    return runtime


def _runtime_config() -> dict[str, Any]:
    data, status, _ = load_bazi_symbolic_layers()
    return discipline_runtime_config(data) if status == "available" else {}


def _empty_score() -> dict[str, Any]:
    return {
        "base_score": 0.0,
        "spirit_delta": 0.0,
        "question_delta": 0.0,
        "final_score": 0.0,
        "evidence": [],
    }


def _apply_spirit_deltas(
    scores: dict[str, dict[str, Any]],
    spirit_sha_analysis: dict[str, Any],
    runtime: dict[str, Any],
) -> None:
    policy = runtime.get("spirit_scoring") or {}
    per_image_totals = {image: 0.0 for image in scores}
    for hit in (spirit_sha_analysis or {}).get("active") or []:
        supports = [image for image in hit.get("supports", []) if image in scores]
        hit_delta = min(
            number(hit.get("score_delta", policy.get("default_hit_delta"))),
            number(policy.get("per_hit_cap")),
        )
        for image in supports:
            remaining = number(policy.get("per_image_cap")) - per_image_totals[image]
            delta = min(hit_delta, remaining)
            if scores[image]["base_score"] <= 0:
                delta = min(delta, number(policy.get("spirit_only_cap")))
            if delta <= 0:
                continue
            scores[image]["spirit_delta"] += delta
            per_image_totals[image] += delta
            scores[image]["evidence"].append(_spirit_evidence(hit, image, delta, runtime))


def _apply_question_deltas(
    scores: dict[str, dict[str, Any]],
    question: str,
    runtime: dict[str, Any],
) -> None:
    if not question:
        return
    evidence_template = runtime.get("question_bias_evidence_template", "")
    for rule in runtime.get("question_image_biases") or []:
        image = rule.get("image")
        keywords = rule.get("keywords") or []
        if image in scores and _has_chart_or_spirit_evidence(scores[image]) and any(
            keyword in question for keyword in keywords
        ):
            scores[image]["question_delta"] += number(rule.get("delta"))
            scores[image]["evidence"].append(format_template(evidence_template, {"image": image}))

    broad = runtime.get("broad_question_bias") or {}
    if any(keyword in question for keyword in broad.get("keywords") or []):
        for image in broad.get("images") or []:
            if image not in scores or not _has_chart_or_spirit_evidence(scores[image]):
                continue
            scores[image]["question_delta"] += number(broad.get("delta"))
            scores[image]["evidence"].append(broad.get("evidence", ""))


def _score_group(
    name: str,
    weights: dict[str, float],
    middle_scores: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    supporting_images: list[str] = []
    spirit_factors: list[str] = []
    structural_evidence: list[str] = []
    has_structural_support = False
    score = 0.0
    for image, weight in weights.items():
        item = middle_scores.get(image) or {}
        image_score = number(item.get("final_score"))
        if image_score <= 0:
            continue
        score += image_score * number(weight)
        supporting_images.append(image)
        if number(item.get("base_score")) > 0:
            has_structural_support = True
            structural_evidence.extend(item.get("evidence") or [])
        if number(item.get("spirit_delta")) > 0:
            spirit_factors.append(format_template(
                runtime.get("spirit_factor_template", ""),
                {"image": image, "delta": round(number(item.get("spirit_delta")), 3)},
            ))
    if not has_structural_support:
        supporting_images = []
        spirit_factors = []
        structural_evidence = []
        score = 0.0
    score = round(score, 3)
    return {
        "name": name,
        "score": score,
        "supporting_images": supporting_images,
        "spirit_factors": spirit_factors,
        "structural_evidence": structural_evidence,
        "weakening_factors": [] if supporting_images else [runtime.get("group_no_support", "")],
        "confidence": _confidence(score, supporting_images, runtime.get("confidence") or {}),
    }


def _is_cross_domain(groups: list[dict[str, Any]], policy: dict[str, Any]) -> bool:
    active = [group for group in groups if group["score"] > 0]
    if len(active) < 2:
        return False
    top, second = active[0], active[1]
    close_threshold = max(
        number(policy.get("close_absolute_min")),
        top["score"] * number(policy.get("close_ratio")),
    )
    if top["score"] - second["score"] <= close_threshold:
        return True
    pairs = {frozenset(pair) for pair in policy.get("pairs") or [] if len(pair) == 2}
    top_n = int(number(policy.get("top_n")))
    for left_index, left in enumerate(active[:top_n]):
        for right in active[left_index + 1:top_n]:
            if frozenset((left["name"], right["name"])) not in pairs:
                continue
            pair_threshold = max(
                number(policy.get("pair_absolute_min")),
                max(left["score"], right["score"]) * number(policy.get("pair_ratio")),
            )
            if abs(left["score"] - right["score"]) <= pair_threshold:
                return True
    return False


def _recommended_mode(
    groups: list[dict[str, Any]],
    cross_domain: bool,
    runtime: dict[str, Any],
) -> str:
    policy = runtime.get("recommended_mode") or {}
    active = [group["name"] for group in groups if group["score"] > 0]
    if not active:
        return policy.get("insufficient", "")
    facts = {"first": active[0], "second": active[1] if len(active) > 1 else ""}
    if cross_domain and len(active) >= 2:
        return format_template(policy.get("cross_template", ""), facts)
    return format_template(policy.get("dominant_template", ""), facts)


def _confidence(score: float, supporting_images: list[str], policy: dict[str, Any]) -> str:
    if score >= number(policy.get("high_min_score")) and len(supporting_images) >= int(
        number(policy.get("high_min_images"))
    ):
        return "high"
    if score >= number(policy.get("medium_min_score")):
        return "medium"
    if score > 0:
        return "low"
    return "none"


def _has_chart_or_spirit_evidence(item: dict[str, Any]) -> bool:
    return number(item.get("base_score")) > 0 or number(item.get("spirit_delta")) > 0


def _spirit_evidence(
    hit: dict[str, Any],
    image: str,
    delta: float,
    runtime: dict[str, Any],
) -> str:
    defaults = runtime.get("spirit_defaults") or {}
    positions = "、".join(hit.get("hit_positions") or []) or defaults.get("positions", "")
    facts = {
        "name": hit.get("name") or defaults.get("name", ""),
        "image": image,
        "strength": hit.get("strength") or defaults.get("strength", ""),
        "basis": hit.get("basis", hit.get("value")) or defaults.get("basis", ""),
        "positions": positions,
        "delta": round(delta, 3),
        "avoid": hit.get("avoid") or defaults.get("avoid", ""),
    }
    return format_template(runtime.get("spirit_evidence_template", ""), facts)


def _base_score(item: dict[str, Any]) -> float:
    for key in ("base_score", "score", "final_score"):
        if key in item:
            return number(item.get(key))
    return 0.0
