# Liuyao Advance Retreat Design

## Goal

Add the v9 进退神 layer for moving lines. The layer identifies whether a moving line changes into a same-element forward branch or backward branch, then interprets that trend through the existing spirit-role chain.

## Boundary

This layer is Liuyao-only. It may use moving lines, original branch, changed-line branch, five-element mapping, and `spirit_role`. It must not use Bazi strength, Daliuren transmission progress, or external timing rules.

## Conservative Rule

Only same-element branch pairs are classified:

- `寅 -> 卯`: advance; `卯 -> 寅`: retreat.
- `巳 -> 午`: advance; `午 -> 巳`: retreat.
- `申 -> 酉`: advance; `酉 -> 申`: retreat.
- `亥 -> 子`: advance; `子 -> 亥`: retreat.

Other transformations, including earth branches and cross-element changes, are `none` for v9. This keeps the layer deterministic and avoids forcing disputed rules.

## Fields

```json
{
  "advance_retreat_analysis": {
    "enabled": true,
    "scope": "进退神只用于动爻趋势，不替代用神链。",
    "by_moving_line": [
      {
        "position": 3,
        "spirit_role": "useful_god",
        "change_type": "advance",
        "from_branch": "寅",
        "to_branch": "卯",
        "role_impact": "support_increases"
      }
    ],
    "unresolved": []
  }
}
```

## Role Impact

- 用神/原神化进: `support_increases`.
- 用神/原神化退: `support_decreases`.
- 忌神/仇神化进: `obstruction_increases`.
- 忌神/仇神化退: `obstruction_decreases`.
- 闲神 or none: `neutral`.
- unresolved role: `ambiguous`.

Completion-chain factor placement:

- `support_increases` and `obstruction_decreases` support outcome.
- `support_decreases` and `obstruction_increases` block outcome.
- `neutral` and `ambiguous` are mixed.

## Prompt Policy

The prompt may use 进退 only when `advance_retreat` is enabled and `advance_retreat_analysis.enabled = true`. It must explain 进退 by role: 用神进 and 忌神进 have opposite meanings.
