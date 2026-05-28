# Liuyao Spirit-Role Completion Design

## Goal

Extend Liuyao v4 into a v5 framework for useful-god completion judgment.

This stage implements the core success/blockage chain:

1. Useful god.
2. Original spirit.
3. Avoiding spirit.
4. Enemy spirit.
5. Neutral spirit.

The purpose is to answer whether the chosen image has support, obstruction, or mixed evidence. It still does not produce deterministic final good/bad judgment or event timing.

## Hard Boundary

This remains Liuyao-only.

Forbidden:

- Bazi day-master strength, ten-god imagery, pattern, climate, remedy, luck, or discipline fields.
- Daliuren four lessons, transmissions, heavenly officers, or Daliuren spirit-sha logic.
- Treating six spirits as final judgment authority.
- Free-form model invention of unsupported Liuyao rules.
- Event timing claims.

This stage does not implement:

- Flying and hidden spirits.
- Three-combination bureau judgment.
- Tomb, absolute, long-life cycle details.
- Advance and retreat spirit.
- Event timing.
- Spirit-sha calculation.

These rules must remain reserved fields only.

## Schema Version

Upgrade:

```json
"schema": "liuyao_chart_v5"
```

Keep v4 fields stable. Add:

```json
{
  "spirit_role_analysis": {},
  "completion_chain": {},
  "reserved_rules": {}
}
```

Add to each `derived_lines[]`:

```json
{
  "spirit_role": "useful_god|original_spirit|avoiding_spirit|enemy_spirit|neutral_spirit",
  "spirit_role_reason": "..."
}
```

## Role Definitions

Use `useful_god_selection.selection_result.main_useful_god` as the primary useful god when present.

If the status is:

- `selected`: use `main_useful_god`.
- `layered`: use `main_useful_god` for the completion chain and keep `auxiliary_useful_gods` as secondary axes.
- `ambiguous`: do not assign a full completion chain; mark `status = ambiguous`.
- `missing`: do not invent hidden spirits; mark `status = missing`.

### Element-Based Role Derivation

The role framework is based on six-relative element classes from the chart lines.

For a selected useful god:

- `useful_god`: lines whose six-relative equals main useful god.
- `original_spirit`: lines whose element generates the useful-god element.
- `avoiding_spirit`: lines whose element controls the useful-god element.
- `enemy_spirit`: lines that control the original-spirit element or generate the avoiding-spirit element.
- `neutral_spirit`: all other lines.

When multiple useful-god lines exist, determine useful-god element from each matching line and preserve multiple role maps if their elements differ. Do not force one element unless all useful-god lines share the same element.

For the first implementation, if multiple useful-god elements differ:

```json
{
  "status": "ambiguous",
  "reason": "主用神多现且五行不同，暂不强行合并原忌仇神。"
}
```

## `spirit_role_analysis`

Example:

```json
{
  "status": "ready",
  "main_useful_god": "官鬼",
  "auxiliary_useful_gods": ["父母"],
  "useful_god_elements": ["水"],
  "role_elements": {
    "useful_god": ["水"],
    "original_spirit": ["金"],
    "avoiding_spirit": ["土"],
    "enemy_spirit": ["火"],
    "neutral_spirit": ["木"]
  },
  "by_line": [
    {
      "position": 2,
      "six_relative": "子孙",
      "element": "土",
      "role": "avoiding_spirit",
      "reason": "本爻土克主用神水，为忌神。",
      "moving": true,
      "effective_strength": "strong",
      "void": false
    }
  ],
  "unresolved": []
}
```

Status values:

- `ready`: a main useful god exists and useful-god element is unambiguous.
- `ambiguous`: useful god is ambiguous or useful-god elements conflict.
- `missing`: useful god is absent and hidden spirits are not implemented.

## Completion Chain

Add `completion_chain` as a structured evidence synthesis.

Example:

```json
{
  "mode": "spirit_role_completion",
  "tendency": "blocked",
  "supporting_factors": [
    {
      "type": "useful_god_present",
      "line": 3,
      "summary": "主用神官鬼上卦。"
    }
  ],
  "blocking_factors": [
    {
      "type": "avoiding_spirit_moving_controls_useful_god",
      "line": 2,
      "target_line": 3,
      "summary": "忌神子孙土发动克官鬼水。"
    }
  ],
  "mixed_factors": [
    {
      "type": "layered_auxiliary",
      "summary": "父母为合同通知辅助轴，需与官鬼岗位主轴分层。"
    }
  ],
  "unresolved": [
    "飞伏未实现，缺失用神不作隐藏补充。",
    "应期未实现，不输出具体日期。"
  ]
}
```

Tendency values:

- `supported`: support exists and no strong obstruction is present.
- `blocked`: strong obstruction is present and support is weak or mixed.
- `mixed`: support and obstruction both have meaningful evidence.
- `insufficient`: role analysis is missing, ambiguous, or evidence is too thin.

### Evidence Rules

Supporting factors:

- useful god is present on a line.
- useful god is strong or very strong.
- useful god is not void.
- original spirit is present and strong.
- original spirit moves and generates useful god.
- moving line generates useful god.
- useful god generates or supports shi line, when relation exists.

Blocking factors:

- useful god is void.
- useful god is weak or very weak.
- avoiding spirit is present and strong.
- avoiding spirit moves and controls useful god.
- moving line controls useful god.
- useful god is month-clashed or day-clashed.
- shi line is void when the question requires the querent's reception.

Mixed factors:

- layered useful-god selection exists.
- useful god has support but is also void or clashed.
- original spirit supports useful god while avoiding spirit also attacks useful god.
- auxiliary useful god points in a different direction from main useful god.

These factors are evidence labels, not final judgment. Prompt must still synthesize cautiously.

## Derived Line Additions

Each line should receive a role label:

```json
{
  "position": 3,
  "six_relative": "官鬼",
  "element": "水",
  "spirit_role": "useful_god",
  "spirit_role_reason": "本爻六亲为主用神官鬼。"
}
```

If role analysis is not ready, use:

```json
{
  "spirit_role": "unresolved",
  "spirit_role_reason": "主用神未定，暂不分配原忌仇神。"
}
```

## Reserved Rules

Add a stable top-level field:

```json
{
  "reserved_rules": {
    "enabled": [],
    "reserved": [
      "flying_hidden",
      "three_combination",
      "twelve_stages",
      "advance_retreat",
      "timing"
    ],
    "labels": {
      "flying_hidden": "飞伏",
      "three_combination": "三合局",
      "twelve_stages": "墓绝长生",
      "advance_retreat": "进退神",
      "timing": "应期"
    },
    "scope": "预留字段；当前不计算飞伏、三合局、墓绝长生、进退神、应期。"
  }
}
```

Prompt must treat these as unavailable unless future chart JSON enables them.

## Prompt Upgrade

Update `liuyao_prompt.md`.

Required constraints:

- Use `spirit_role_analysis` after `useful_god_selection`.
- Use `completion_chain` as the main success/blockage evidence layer.
- First analyze useful god, then original spirit, then avoiding spirit, then enemy spirit.
- Moving lines must be interpreted by `spirit_role` before six-spirit imagery.
- Six spirits remain auxiliary presentation style only.
- Do not infer flying/hidden spirits, three-combination bureau, twelve stages, advance/retreat spirit, or timing unless `reserved_rules.enabled` includes them and concrete fields exist.
- Do not output a concrete event date, month, or day in this stage.

Prompt section changes:

- `用神定位`: include useful-god status and whether role analysis is ready.
- `旺衰与月日`: include role-aware strength; e.g. useful god weak, avoiding spirit strong.
- `动变作用`: explain moving line role first; e.g. moving avoiding spirit attacks useful god.
- `综合倾向`: use `completion_chain.tendency` and evidence factors.
- `不确定项`: mention reserved rules remain unavailable.

## Tests

Add tests for:

1. Role derivation:
   - `离之大有`, `问工作 offer 合同什么时候下来`, `壬寅日`
   - main useful god `官鬼` is water.
   - useful-god line 3 is `useful_god`.
   - line 2 `子孙` earth is `avoiding_spirit`.
   - line 4 `妻财` metal is `original_spirit`.
   - line 6 `兄弟` fire is `enemy_spirit`.

2. Completion chain:
   - same chart.
   - useful god present appears as support.
   - moving line 2 earth controls useful-god line 3 water and appears as blocking.
   - tendency is `blocked` or `mixed`; it must not be `supported`.

3. Derived line attachment:
   - every `derived_lines[]` has `spirit_role` and `spirit_role_reason`.

4. Reserved rules:
   - `reserved_rules.enabled == []`.
   - reserved includes `flying_hidden`, `three_combination`, `twelve_stages`, `advance_retreat`, `timing`.

5. Prompt policy:
   - prompt requires `spirit_role_analysis` and `completion_chain`.
   - prompt states moving lines must be interpreted by role before six spirit.
   - prompt forbids concrete event timing in this stage.

6. Boundary:
   - v5 JSON contains no Bazi or Daliuren fields.
   - full project tests pass.

## Acceptance Criteria

- `liuyao_chart_v5` is emitted.
- v4 fields remain stable.
- `spirit_role_analysis.status` is deterministic.
- Every derived line has role metadata.
- `completion_chain` summarizes support/blockage/mixed evidence without final deterministic judgment.
- Reserved advanced rules are explicit but disabled.
- Prompt prevents unsupported flying spirits, combinations, twelve stages, advance/retreat, and timing.
- Full Liuyao tests and full project tests pass.
