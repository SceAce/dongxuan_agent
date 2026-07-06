# Liuyao Timing Candidate Design

## Goal

Add v10 应期 as bounded timing candidates. The engine should emit branch-based timing triggers from existing Liuyao evidence, but it must not convert them into Gregorian dates or assert a single final date.

## Boundary

Allowed inputs:

- `derived_lines`, especially spirit roles, void state, moving state, and changed branch;
- `combination_analysis`;
- `flying_hidden_analysis`;
- `advance_retreat_analysis`;
- calendar day/month branches and xunkong.

Disallowed:

- Bazi annual luck or flow-year logic;
- Daliuren transmissions;
- web lookup;
- concrete Gregorian date generation.

## Candidate Rules

Emit timing candidates with branch, basis, source, confidence, and caution.

Rules:

- Void useful/original line: candidate branches are the void branch itself for `value_when_filled`, and the clash branch for `clash_void`.
- Moving useful/original/avoiding/enemy line: candidate changed branch for `changed_branch_value`.
- Three-combination pending or half group: missing branches as `combination_completion`.
- Hidden useful/original spirit: hidden branch as `hidden_spirit_value`; flying branch clash as `clash_flying`.
- Advance/retreat moving line: changed branch as `advance_retreat_value`.

The layer must dedupe same branch+basis+source references.

## Fields

```json
{
  "timing_analysis": {
    "enabled": true,
    "scope": "应期只输出地支候选触发点，不输出公历日期。",
    "candidates": [
      {
        "branch": "午",
        "basis": "advance_retreat_value",
        "source": "advance_retreat_analysis",
        "line": 2,
        "spirit_role": "useful_god",
        "confidence": "medium",
        "caution": "候选应期需结合现实周期，不等于确定日期。"
      }
    ],
    "unresolved": [
      "当前不换算公历日期。"
    ]
  }
}
```

## Prompt Policy

The prompt may discuss 应期 only from `timing_analysis.candidates`. It must say these are branch-trigger candidates and must not output exact Gregorian dates, months, or years unless a future tool layer supplies conversion fields.
