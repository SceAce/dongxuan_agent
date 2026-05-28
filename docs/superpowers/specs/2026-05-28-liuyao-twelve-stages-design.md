# Liuyao Twelve Stages Design

## Goal

Implement v6 十二长生 as the second enabled layer in the advanced Liuyao judgment chain.

This layer attaches a twelve-stage state to every derived line by comparing the line element and line branch. It modifies role-chain strength evidence, but it does not select useful gods and does not decide final good/bad outcomes.

## Scope

Enable:

- `twelve_stages` in `advanced_layers.enabled`.
- `twelve_stage` on each `derived_lines[]`.
- `twelve_stage_analysis` as role-aware summary evidence.

Keep reserved:

- 三合
- 飞伏
- 进退
- 应期
- 神煞

## Rule Basis

Use 爻地支五行十二长生.

Table:

```json
{
  "木": ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"],
  "火": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
  "土": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
  "金": ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"],
  "水": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
}
```

Stage order:

```json
["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]
```

## Output Fields

Each line receives:

```json
{
  "twelve_stage": {
    "stage": "临官",
    "element": "水",
    "branch": "亥",
    "strength_hint": "growth",
    "scope": "状态辅助，不直接定吉凶"
  }
}
```

Add top-level:

```json
{
  "twelve_stage_analysis": {
    "enabled": true,
    "scope": "状态辅助，不直接定吉凶",
    "by_role": [],
    "supporting_factors": [],
    "blocking_factors": [],
    "mixed_factors": []
  }
}
```

## Strength Hints

- `长生`, `冠带`, `临官`: `growth`
- `帝旺`: `peak`
- `沐浴`: `unstable`
- `衰`, `病`: `decline`
- `死`, `绝`: `cutoff`
- `墓`: `storage`
- `胎`, `养`: `incubation`

## Role Integration

The stage must be interpreted through `spirit_role`.

Examples:

- 用神临官/帝旺: useful-god state support.
- 忌神临官/帝旺: obstruction state support.
- 原神长生/临官/帝旺: source support.
- 仇神长生/临官/帝旺: obstruction-side support.
- 用神墓/绝/死: useful-god state blockage.

`completion_chain` may include twelve-stage evidence only when `twelve_stages` is enabled.

## Prompt Rules

- Use 十二长生 only after `spirit_role_analysis`.
- Do not treat 十二长生 as final good/bad judgment.
- Do not use 十二长生 unless `advanced_layers.enabled` contains `twelve_stages`.
- Explain stage by role: 用神、原神、忌神、仇神、闲神.

## Tests

- `水` at `亥` is `临官`.
- `土` at `丑` is `衰`.
- `金` at `酉` is `帝旺`.
- Every derived line has `twelve_stage`.
- `advanced_layers.enabled == ["spirit_roles", "twelve_stages"]`.
- `three_combination`, `flying_hidden`, `advance_retreat`, `timing`, and `spirit_sha` remain reserved.
- Prompt requires role-aware twelve-stage use.
