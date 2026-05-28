# Liuyao Flying Hidden Design

## Goal

Add the v8 飞伏 layer to the Liuyao chart engine so missing six-relative images can be surfaced as deterministic hidden spirits, then interpreted only through the existing 用神/原神/忌神/仇神/闲神 chain.

## Position In The Advanced Chain

The enabled order becomes:

1. `spirit_roles`
2. `twelve_stages`
3. `three_combination`
4. `flying_hidden`

Reserved layers remain:

1. `advance_retreat`
2. `timing`
3. `spirit_sha`

The prompt may use 飞伏 only when `advanced_layers.enabled` contains `flying_hidden` and `flying_hidden_analysis.enabled = true`.

## Rule Source Boundary

This layer is Liuyao-only. It may use:

- the original hexagram;
- eight-palace metadata;
- najia stem-branch tables;
- six-relative calculation from palace element;
- existing five-element generating/controlling relations;
- existing spirit-role analysis.

It must not use Bazi day-master strength, Daliuren lessons/transmissions, or any external web lookup.

## Hidden Spirit Mapping

`najia.hidden_spirits` is no longer an empty compatibility field. It is generated from the original hexagram's palace:

1. Find the original hexagram's palace, for example `乾宫`.
2. Resolve that palace's pure palace hexagram, for example `乾为天`.
3. Build the pure palace hexagram's six najia lines with the same palace element.
4. Compare the original hexagram's visible six relatives with the pure palace lines.
5. For every pure palace line whose six relative is missing from the original hexagram, emit a hidden spirit under the same position.
6. The visible line at that position is the flying spirit.

This means 飞伏 only fills missing six relatives. If all five six relatives are visible, `hidden_spirits` is an empty list and the layer reports no hidden useful-god support.

Each hidden item contains:

```json
{
  "position": 1,
  "name": "初爻",
  "hidden_stem_branch": "甲子",
  "hidden_branch": "子",
  "hidden_element": "水",
  "hidden_six_relative": "子孙",
  "flying_stem_branch": "乙未",
  "flying_branch": "未",
  "flying_element": "土",
  "flying_six_relative": "父母",
  "source_palace_hexagram": "乾为天"
}
```

## Flying Hidden Analysis

`flying_hidden_analysis` interprets hidden spirits without replacing visible-line judgment.

Top-level shape:

```json
{
  "enabled": true,
  "scope": "飞伏只补缺失六亲与隐藏用神，不替代上卦用神和动变主线。",
  "hidden_lines": [],
  "hidden_useful_gods": [],
  "relations": [],
  "unresolved": []
}
```

For each hidden spirit:

- attach `hidden_spirits` to the matching `derived_lines[]`;
- compute `hidden_role_impact` from `spirit_role_analysis.role_elements`;
- compute flying-to-hidden element relation;
- compute hidden-to-flying element relation.

Relation impact policy:

- hidden useful god or original spirit is supporting only when the flying spirit generates it or is same element;
- hidden useful god or original spirit is mixed when flying controls it or hidden controls flying;
- hidden avoiding spirit or enemy spirit is blocking when it is supported or has force against a useful/original chain;
- hidden neutral spirit is mixed or neutral and never decides the outcome.

If `spirit_role_analysis.status != "ready"`, the layer remains enabled but marks role impact as `mixed` and explains that the main useful-god chain is unresolved.

## Completion Chain

`completion_chain` accepts flying-hidden factors after twelve stages and three combinations. It must not delete earlier support/blocking evidence.

Supporting factor examples:

- `hidden_useful_god_supported_by_flying`
- `hidden_original_spirit_supported_by_flying`

Blocking factor examples:

- `hidden_useful_god_controlled_by_flying`
- `hidden_avoiding_spirit_supported`

Mixed factor examples:

- `hidden_useful_god_present_but_buried`
- `hidden_role_unresolved`

The chain unresolved list must remove the previous blanket message "飞伏未实现，缺失用神不作隐藏补充。" after v8 is enabled. Timing remains unresolved.

## Prompt Policy

The prompt must state:

- 飞伏 is available only through `flying_hidden_analysis`.
- Hidden spirits are evidence only for missing or buried images.
- Visible useful gods, 世应, 月日, 动变, 十二长生, and 三合 remain earlier evidence.
- The model may not invent hidden spirits beyond `najia.hidden_spirits`.
- The model may not output concrete timing because `timing` is still reserved.

## Tests

Use a hexagram with missing relatives, such as `天地否` in `乾宫`, where visible lines miss `子孙`. The palace pure hexagram `乾为天` supplies `甲子` 子孙 at 初爻, hidden under the visible 初爻 父母未.

Required tests:

- `build_najia("天地否")` emits a hidden 子孙 at 初爻 from `乾为天`.
- a question whose main useful god is 子孙 receives hidden useful-god evidence rather than a missing-only unresolved result;
- the payload schema becomes `liuyao_chart_v8`;
- `advanced_layers.enabled` includes `flying_hidden`;
- prompt contract requires `flying_hidden_analysis`;
- prompt text forbids invented hidden spirits and still forbids timing.
