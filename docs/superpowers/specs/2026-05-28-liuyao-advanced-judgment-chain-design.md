# Liuyao Advanced Judgment Chain Design

## Goal

Build the next Liuyao judgment system as a staged chain:

1. 原忌仇用闲神
2. 十二长生
3. 三合
4. 飞伏
5. 进退
6. 应期
7. 神煞

The chain must improve judgment accuracy without letting later auxiliary rules override the core useful-god structure.

## Core Principle

Every later layer depends on the earlier layers.

The interpretation order is:

```text
用神主轴 -> 成败生克链 -> 状态强弱 -> 组合动变 -> 缺失补位 -> 进退趋势 -> 应期候选 -> 神煞旁证
```

Rules:

- 原忌仇用闲神 is the primary judgment skeleton.
- 十二长生 modifies state, not the identity of the useful god.
- 三合 modifies grouped force, not useful-god selection.
- 飞伏 is only meaningful after missing or hidden useful-god cases are identified.
- 进退 is only meaningful for moving/changing lines.
- 应期 is only allowed after role, state, movement, and availability are computed.
- 神煞 is last and auxiliary; it cannot override role-chain evidence.

## Hard Boundary

This remains Liuyao-only.

Forbidden:

- Bazi day-master strength, ten-god imagery, pattern, climate, remedy, luck, or discipline fields.
- Daliuren four lessons, transmissions, heavenly officers, or Daliuren spirit-sha logic.
- Six spirits or spirit-sha as final judgment authority.
- Event timing before the timing layer is enabled.
- Free-form model invention of unsupported rules.

The prompt must use emitted JSON fields only. If a layer is not enabled or lacks concrete data, the model must mark it unavailable.

## Schema Strategy

The implementation may either:

- keep a single `liuyao_chart_v5` schema while adding staged fields, or
- increment schema versions per stage.

Recommended:

- `liuyao_chart_v5`: 原忌仇用闲神 + reserved layer contracts.
- `liuyao_chart_v6`: 十二长生.
- `liuyao_chart_v7`: 三合.
- `liuyao_chart_v8`: 飞伏.
- `liuyao_chart_v9`: 进退.
- `liuyao_chart_v10`: 应期.
- `liuyao_chart_v11`: 神煞.

Each stage must keep earlier fields stable.

Field examples below describe the payload shape after that specific layer is implemented. Before a layer is implemented, it must stay out of evidence fields and remain listed in `advanced_layers.reserved`.

## Layer 1: 原忌仇用闲神

### Purpose

Create the core completion chain. This layer determines whether the selected useful god is supported, obstructed, mixed, or insufficient.

### New Fields

```json
{
  "spirit_role_analysis": {},
  "completion_chain": {}
}
```

Each `derived_lines[]` receives:

```json
{
  "spirit_role": "useful_god|original_spirit|avoiding_spirit|enemy_spirit|neutral_spirit|unresolved",
  "spirit_role_reason": "..."
}
```

### Role Definitions

Use `useful_god_selection.selection_result.main_useful_god` as the main useful god.

If useful-god selection is:

- `selected`: assign roles normally.
- `layered`: assign roles using the main useful god; keep auxiliary gods as secondary axes.
- `ambiguous`: do not assign full roles; mark unresolved.
- `missing`: do not invent hidden spirits; wait for 飞伏 layer.

For selected useful-god element:

- `用神`: same six-relative as main useful god.
- `原神`: element that generates the useful-god element.
- `忌神`: element that controls the useful-god element.
- `仇神`: element that controls original-spirit element or generates avoiding-spirit element.
- `闲神`: remaining lines.

If multiple useful-god lines have different elements, mark role analysis `ambiguous`.

### Completion Chain

Use evidence labels:

- `supporting_factors`
- `blocking_factors`
- `mixed_factors`
- `unresolved`

Tendency values:

- `supported`
- `blocked`
- `mixed`
- `insufficient`

This is still not a final deterministic judgment.

## Layer 2: 十二长生

### Purpose

Add state modifiers for each line by comparing the line element and line branch.

The user confirmed the rule basis: use 爻地支五行十二长生.

### Long-Life Table

Use the traditional five-element table:

```json
{
  "木": {
    "长生": "亥",
    "沐浴": "子",
    "冠带": "丑",
    "临官": "寅",
    "帝旺": "卯",
    "衰": "辰",
    "病": "巳",
    "死": "午",
    "墓": "未",
    "绝": "申",
    "胎": "酉",
    "养": "戌"
  },
  "火": {
    "长生": "寅",
    "沐浴": "卯",
    "冠带": "辰",
    "临官": "巳",
    "帝旺": "午",
    "衰": "未",
    "病": "申",
    "死": "酉",
    "墓": "戌",
    "绝": "亥",
    "胎": "子",
    "养": "丑"
  },
  "土": {
    "长生": "申",
    "沐浴": "酉",
    "冠带": "戌",
    "临官": "亥",
    "帝旺": "子",
    "衰": "丑",
    "病": "寅",
    "死": "卯",
    "墓": "辰",
    "绝": "巳",
    "胎": "午",
    "养": "未"
  },
  "金": {
    "长生": "巳",
    "沐浴": "午",
    "冠带": "未",
    "临官": "申",
    "帝旺": "酉",
    "衰": "戌",
    "病": "亥",
    "死": "子",
    "墓": "丑",
    "绝": "寅",
    "胎": "卯",
    "养": "辰"
  },
  "水": {
    "长生": "申",
    "沐浴": "酉",
    "冠带": "戌",
    "临官": "亥",
    "帝旺": "子",
    "衰": "丑",
    "病": "寅",
    "死": "卯",
    "墓": "辰",
    "绝": "巳",
    "胎": "午",
    "养": "未"
  }
}
```

### New Fields

Each `derived_lines[]` receives:

```json
{
  "twelve_stage": {
    "stage": "长生|沐浴|冠带|临官|帝旺|衰|病|死|墓|绝|胎|养",
    "element": "水",
    "branch": "亥",
    "strength_hint": "growth|peak|decline|storage|cutoff|incubation",
    "scope": "状态辅助，不直接定吉凶"
  }
}
```

Prompt must not treat 十二长生 as final judgment. It modifies role-chain evidence.

## Layer 3: 三合

### Purpose

Detect whether line branches form 三合, 半合, or 待合 and whether the combination strengthens useful-god, original-spirit, avoiding-spirit, or enemy-spirit roles.

### Supported Groups

```json
{
  "申子辰": "水",
  "亥卯未": "木",
  "寅午戌": "火",
  "巳酉丑": "金"
}
```

### New Fields

```json
{
  "combination_analysis": {
    "enabled": true,
    "groups": [
      {
        "type": "full_three_combination|half_combination|pending_combination",
        "branches": ["巳", "酉", "丑"],
        "element": "金",
        "line_positions": [2, 4],
        "role_impact": "supports_original_spirit|supports_useful_god|supports_avoiding_spirit|mixed|neutral",
        "reason": "..."
      }
    ]
  }
}
```

三合 cannot override useful-god selection. It only modifies force direction.

## Layer 4: 飞伏

### Purpose

Handle missing useful gods and hidden availability.

This layer is only meaningful when:

- useful god is absent,
- auxiliary useful god is absent,
- or a role needed by completion chain is absent.

### New Fields

```json
{
  "flying_hidden_analysis": {
    "enabled": true,
    "hidden_lines": [],
    "flying_hidden_relations": [],
    "availability": "available|blocked|ambiguous|not_applicable"
  }
}
```

Rules:

- Do not invent hidden spirits unless the chart engine emits them.
- If hidden-spirit mapping is incomplete, mark `ambiguous`.
- 飞神/伏神生克 should feed into `completion_chain`, not replace it.

## Layer 5: 进退

### Purpose

Evaluate moving lines that change into progress or retreat.

This layer applies only to moving lines.

### New Fields

```json
{
  "advance_retreat_analysis": {
    "enabled": true,
    "by_moving_line": [
      {
        "position": 2,
        "spirit_role": "avoiding_spirit",
        "change_type": "advance|retreat|none|ambiguous",
        "from_branch": "丑",
        "to_branch": "寅",
        "role_impact": "obstruction_increases|obstruction_decreases|support_increases|support_decreases|neutral"
      }
    ]
  }
}
```

Prompt must interpret 进退 by role:

- 用神进 is not the same as 忌神进.
- 原神退 is not the same as 忌神退.

## Layer 6: 应期

### Purpose

Generate timing candidates after role, stage, combination, hidden availability, and advance/retreat are available.

### New Fields

```json
{
  "timing_analysis": {
    "enabled": true,
    "candidates": [
      {
        "basis": "冲空|合动|值临|墓绝|进退|飞伏",
        "branch": "亥",
        "time_unit": "day|month|year|unknown",
        "confidence": "strong|medium|weak",
        "reason": "...",
        "caution": "候选应期，不作保证"
      }
    ],
    "unresolved": []
  }
}
```

Rules:

- Do not output one guaranteed time.
- Output candidates with basis and confidence.
- If evidence conflicts, mark `unknown` or `weak`.
- Timing must never appear before this layer is enabled.

## Layer 7: 神煞

### Purpose

Add auxiliary imagery and timing side evidence after all structural layers.

### Initial Scope

Keep the initial enabled set small:

- 驿马: movement/change.
- 桃花: attraction/relationship/social image.
- 贵人: assistance/support.

### New Fields

```json
{
  "spirit_sha_analysis": {
    "enabled": true,
    "active": [
      {
        "name": "驿马",
        "line_position": 3,
        "attached_to_role": "useful_god",
        "meaning": "movement/change",
        "scope": "辅助旁证"
      }
    ]
  }
}
```

Rules:

- 神煞 cannot override role-chain evidence.
- Inactive spirit-sha must not be listed.
- Active spirit-sha must attach to a line and role.

## Reserved Layer Contract

Until a layer is implemented, keep it in:

```json
{
  "advanced_layers": {
    "enabled": ["spirit_roles"],
    "reserved": [
      "twelve_stages",
      "three_combination",
      "flying_hidden",
      "advance_retreat",
      "timing",
      "spirit_sha"
    ],
    "order": [
      "spirit_roles",
      "twelve_stages",
      "three_combination",
      "flying_hidden",
      "advance_retreat",
      "timing",
      "spirit_sha"
    ],
    "scope": "Only enabled layers may be used as evidence."
  }
}
```

Each implementation stage moves one layer from `reserved` to `enabled`.

## Prompt Contract

Prompt must enforce:

- Use layers in `advanced_layers.order`.
- Use only layers listed in `advanced_layers.enabled`.
- If a later layer conflicts with an earlier layer, earlier structural evidence wins unless the later layer explains a concrete mechanism.
- Six spirits and spirit-sha are auxiliary only.
- No timing unless `timing_analysis.enabled = true`.
- No hidden-spirit reasoning unless `flying_hidden_analysis.enabled = true`.
- No 三合 reasoning unless `combination_analysis.enabled = true`.
- No 十二长生 reasoning unless `twelve_stage` exists on lines.
- No 进退 reasoning unless `advance_retreat_analysis.enabled = true`.

## Implementation Strategy

Implement one layer per plan/spec stage.

Recommended next implementation:

1. v5 原忌仇用闲神 + `advanced_layers`.
2. v6 十二长生.
3. v7 三合.
4. v8 飞伏.
5. v9 进退.
6. v10 应期.
7. v11 神煞.

Do not implement multiple later layers in the same task unless earlier layer tests already pass.

## Tests

Every stage must include:

- Unit tests for the new rule module.
- Payload integration tests.
- Prompt policy tests.
- Boundary tests ensuring disabled layers are not used.
- CLI sample verification.
- Full Liuyao and full project tests.

Critical cross-stage tests:

- Later layer disabled means prompt cannot mention it as evidence.
- 神煞 cannot override 原忌仇用闲神 evidence.
- 应期 candidates cannot exist before timing layer is enabled.
- 飞伏 cannot invent hidden spirits without chart data.
- 三合 must attach to concrete line positions and role impact.
- 十二长生 must attach to each line and remain a state modifier.

## Acceptance Criteria

- The advanced chain has a stable ordered contract.
- Each layer has explicit enabled/reserved state.
- v5 implementation can start with 原忌仇用闲神 without blocking later layers.
- 十二长生 uses the confirmed 爻地支五行十二长生 table.
- Prompt cannot skip ahead to disabled rules.
- Bazi and Daliuren systems remain isolated.
