# Liuyao Three Combination Design

## Goal

Implement v7 三合 as the third enabled layer in the Liuyao advanced judgment chain.

This layer detects full three-combination, half-combination, and pending-combination patterns among line branches, then maps each group to a role impact through the already-established spirit-role chain.

## Scope

Enable:

- `three_combination` in `advanced_layers.enabled`.
- `combination_analysis` top-level field.

Keep reserved:

- 飞伏
- 进退
- 应期
- 神煞

## Supported Groups

```json
{
  "申子辰": "水",
  "亥卯未": "木",
  "寅午戌": "火",
  "巳酉丑": "金"
}
```

## Group Types

- `full_three_combination`: all three branches appear on chart lines.
- `half_combination`: two branches from a group appear on chart lines.
- `pending_combination`: one branch appears on chart lines and another required branch is month or day branch.

Do not create a group from month/day branches alone. At least one chart line must participate.

## Output

```json
{
  "combination_analysis": {
    "enabled": true,
    "scope": "三合只修正合力方向，不替代用神选择。",
    "groups": [
      {
        "type": "half_combination",
        "branches": ["巳", "酉"],
        "missing_branches": ["丑"],
        "element": "金",
        "line_positions": [4, 6],
        "external_branches": [],
        "role_impact": "supports_original_spirit",
        "reason": "巳酉半合金，金为原神，属支持侧合力。"
      }
    ]
  }
}
```

## Role Impact

Map combination element against `spirit_role_analysis.role_elements`:

- element equals useful-god element: `supports_useful_god`
- element equals original-spirit element: `supports_original_spirit`
- element equals avoiding-spirit element: `supports_avoiding_spirit`
- element equals enemy-spirit element: `supports_enemy_spirit`
- otherwise: `neutral`

If multiple role elements exist or role analysis is not ready, use `mixed`.

## Completion Chain Integration

Combination evidence may be added to `completion_chain`:

- useful-god or original-spirit combinations -> supporting factors.
- avoiding-spirit or enemy-spirit combinations -> blocking factors.
- neutral or mixed combinations -> mixed factors.

三合 cannot override:

- useful-god selection
- spirit-role assignment
- direct moving-line control/generation evidence

## Prompt Rules

- Use 三合 only when `advanced_layers.enabled` includes `three_combination`.
- 三合 must attach to concrete line positions and branches.
- 三合 must be interpreted by `role_impact`.
- Do not say 三合 alone makes the matter good or bad.
- Do not infer missing branches beyond `missing_branches`.

## Tests

- `离之大有` contains `巳` and `酉`, so it produces a `巳酉` half-combination for 金.
- In the work-offer sample, 金 is original spirit, so role impact is `supports_original_spirit`.
- `combination_analysis.enabled` is true.
- `advanced_layers.enabled == ["spirit_roles", "twelve_stages", "three_combination"]`.
- `flying_hidden`, `advance_retreat`, `timing`, and `spirit_sha` remain reserved.
- Prompt requires role-aware 三合 use and forbids 三合-only final judgment.
