# Liuyao Spirit Sha Design

## Goal

Add v11 神煞 as a bounded auxiliary layer. Implement only three stable marks: 天乙贵人, 驿马, 桃花. These marks may refine imagery and weighting, but must never override useful-god, spirit-role, strength, moving, flying-hidden, advance-retreat, or timing evidence.

## Rules

天乙贵人 uses day stem:

- 甲戊: 丑、未
- 乙己: 子、申
- 丙丁: 亥、酉
- 庚辛: 午、寅
- 壬癸: 卯、巳

驿马 uses day branch group:

- 申子辰: 寅
- 寅午戌: 申
- 亥卯未: 巳
- 巳酉丑: 亥

桃花 uses day branch group:

- 申子辰: 酉
- 寅午戌: 卯
- 巳酉丑: 午
- 亥卯未: 子

## Fields

`auxiliary_marks.enabled` becomes `["天乙贵人", "驿马", "桃花"]`.

Add:

```json
{
  "spirit_sha_analysis": {
    "enabled": true,
    "scope": "神煞只作辅助取象与旁证，不作主裁决。",
    "marks": [
      {
        "name": "驿马",
        "branch": "寅",
        "matched_lines": [],
        "meaning": "行动、变动、远行、消息流动",
        "role_impacts": []
      }
    ],
    "unresolved": []
  }
}
```

Each matched line gets `spirit_sha_marks`.

## Prompt Policy

The prompt must use 神煞 only after the main completion chain. It must state that 神煞 is auxiliary and cannot decide outcome alone.
