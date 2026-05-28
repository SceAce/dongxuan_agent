# Liuyao Tool MVP Design

## Goal

Build a Liuyao tool MVP that can create a structured Liuyao chart from manual hexagram input, six line results, or random line generation.

The first version focuses on stable tooling and JSON structure, not final divination judgment. It should provide enough structured context for later prompt-based analysis:

- Original hexagram and changed hexagram.
- Six lines from bottom to top.
- Moving lines and changed line states.
- Palace, shi/ying, najia, six relatives, and missing relatives.
- Question domain and candidate useful gods.
- Basic analysis hints that tell the model what to inspect next.

## Hard Boundary

Liuyao must remain independent from Bazi and Daliuren analysis.

Allowed shared dependency:

- Calendar ganzhi calculation from `dongxuan_agent.calendar_engine`, only for year/month/day/hour ganzhi, month branch, day branch, and xunkong.

Forbidden Bazi fields in Liuyao JSON:

- `strength_analysis`
- `climate_analysis`
- `pattern_analysis`
- `remedy_analysis`
- `god_candidates`
- `luck_year_remedy`
- `discipline_profile`

Forbidden Daliuren fields in Liuyao JSON:

- `four_lessons`
- `transmissions`
- `heavenly_officers`
- Daliuren `spirit_sha.active` hit logic based on four lessons or transmissions

Liuyao may only reason through Liuyao-native structure:

- Hexagram and changed hexagram.
- Six lines.
- Najia.
- Six relatives.
- Shi/ying.
- Month branch and day branch.
- Moving and changed lines.
- Candidate useful gods.

## Non-Goals

The MVP does not implement:

- Final auspicious/inauspicious judgment.
- Detailed month/day prosperity and decline scoring.
- Full flying/hidden spirit interaction judgment.
- Six spirits.
- Spirit-sha.
- Event timing.
- Multi-school rule variants.
- Time-based hexagram generation.

Time-based hexagram generation can be added after the manual/random line flows are stable.

## Inputs

### 1. Named Hexagram Input

Supported examples:

- `离之大有`
- `离为火之火天大有`
- `离卦二爻动得大有卦`

Rules:

- If original and changed hexagram names are both supplied, the tool derives moving lines from the line differences.
- If original hexagram and moving line positions are supplied, the tool derives the changed hexagram.
- If original, moving lines, and changed hexagram are supplied, they must be internally consistent.
- If the relationship is inconsistent, return a clear error instead of silently correcting the chart.

### 2. Manual Six-Line Results

Supported example:

```text
少阳 老阴 少阴 少阳 老阳 少阴
```

Line order is always bottom to top:

1. 初爻
2. 二爻
3. 三爻
4. 四爻
5. 五爻
6. 上爻

Line states:

- `少阳`: yang, not moving.
- `老阳`: yang, moving, changes to yin.
- `少阴`: yin, not moving.
- `老阴`: yin, moving, changes to yang.

If the user supplies fewer or more than six results, the tool must return an error that states the expected order.

### 3. Random Six-Line Generation

The tool supports random line generation for users who cannot correctly use coins or other casting tools.

Default probability follows the three-coin method:

- `老阴`: 1/8
- `少阳`: 3/8
- `少阴`: 3/8
- `老阳`: 1/8

The output must preserve each generated line result. It must not output only the original and changed hexagram names.

## Output JSON

Top-level shape:

```json
{
  "schema": "liuyao_chart_v1",
  "input": {},
  "calendar": {},
  "hexagram": {},
  "lines": [],
  "palace": {},
  "najia": {},
  "question_context": {},
  "analysis_hints": {},
  "uncertainty": []
}
```

### `input`

```json
{
  "method": "manual_lines",
  "raw": "少阳 老阴 少阴 少阳 老阳 少阴",
  "line_order": "bottom_to_top",
  "question": "问工作"
}
```

`method` values:

- `manual_lines`
- `named_hexagram`
- `random_lines`

### `calendar`

```json
{
  "datetime": "2026-05-28T09:30:00+08:00",
  "timezone": "Asia/Shanghai",
  "year_gz": "丙午",
  "month_gz": "癸巳",
  "day_gz": "壬子",
  "hour_gz": "乙巳",
  "month_branch": "巳",
  "day_branch": "子",
  "xunkong": ["寅", "卯"]
}
```

This section is only a calendar reference. It must not trigger Bazi-style strength, pattern, remedy, or luck analysis.

### `hexagram`

```json
{
  "original": {
    "name": "离为火",
    "upper_trigram": "离",
    "lower_trigram": "离",
    "binary_bottom_to_top": "101101"
  },
  "changed": {
    "name": "火天大有",
    "upper_trigram": "离",
    "lower_trigram": "乾",
    "binary_bottom_to_top": "111101"
  },
  "moving_lines": [2],
  "description": "离卦二爻动，变火天大有"
}
```

Binary convention:

- Six characters, bottom to top.
- `1` means yang.
- `0` means yin.

### `lines`

The six lines are always bottom to top:

```json
[
  {
    "position": 1,
    "name": "初爻",
    "input_state": "少阳",
    "yin_yang": "阳",
    "moving": false,
    "changed_yin_yang": "阳"
  },
  {
    "position": 2,
    "name": "二爻",
    "input_state": "老阴",
    "yin_yang": "阴",
    "moving": true,
    "changed_yin_yang": "阳"
  }
]
```

### `palace`

```json
{
  "palace": "离宫",
  "generation": "本宫卦",
  "shi_position": 6,
  "ying_position": 3,
  "shi_line": "上爻",
  "ying_line": "三爻"
}
```

The first implementation must use one consistent Jing Fang eight-palace mapping for palace, generation, shi, and ying. If a mapping entry is missing, the chart should fail with a clear implementation error instead of guessing.

### `najia`

```json
{
  "palace_element": "火",
  "lines": [
    {
      "position": 1,
      "stem_branch": "己卯",
      "branch": "卯",
      "element": "木",
      "six_relative": "子孙",
      "role": null
    },
    {
      "position": 3,
      "role": "应"
    },
    {
      "position": 6,
      "role": "世"
    }
  ],
  "missing_relatives": ["妻财"],
  "hidden_spirits": []
}
```

Six relatives are computed from the hexagram palace element as the self element, using Liuyao six-relative relationships. This must not call Bazi day-master or strength logic.

`hidden_spirits` can be an empty list in the MVP, but the field should exist for compatibility with later flying/hidden spirit work.

### `question_context`

```json
{
  "domain": "事业/工作",
  "candidate_useful_gods": [
    {
      "six_relative": "官鬼",
      "reason": "事业、职位、规则压力以官鬼为主要候选用神"
    },
    {
      "six_relative": "父母",
      "reason": "合同、文书、单位、证书可取父母为辅助候选"
    }
  ],
  "avoid": [
    "候选用神不等于最终用神，必须结合世应、动爻、月日旺衰和生克关系。"
  ]
}
```

The MVP only classifies question domain and useful-god candidates. It does not select the final useful god.

### `analysis_hints`

```json
{
  "moving_summary": "二爻动，阴变阳",
  "shi_ying_summary": "世在上爻，应在三爻",
  "useful_god_candidates": [],
  "must_check": [
    "月建日辰对用神、世爻、应爻的生克冲合",
    "动爻对世应和候选用神的作用",
    "变爻是否回头生克"
  ]
}
```

Hints should orient the model toward Liuyao checks without deciding final judgment.

## Prompt Boundary

Create `liuyao_prompt.md` with these rules:

- JSON is the only chart source.
- Do not change original hexagram, changed hexagram, moving lines, line order, najia, six relatives, palace, shi, or ying.
- Do not use Bazi strength/pattern/remedy/luck logic.
- Do not use Daliuren four lessons, transmissions, heavenly officers, or Daliuren spirit-sha logic.
- Candidate useful gods are candidates only; final useful god requires checking question domain, shi/ying, moving lines, month/day, and six-relative interactions.
- First analysis should state the chart structure and useful-god candidates, then list what must be checked.
- If a field is missing, mark it uncertain instead of fabricating a rule result.

## CLI And Session Tools

Add scripts matching the existing project style:

- `liuyao-chart`: chart-only JSON/markdown output.
- `liuyao_session.py`: context JSON plus optional prompt.
- `tools_liuyao_chart_wrapper.py`: wrapper for tool calling.
- `tools_liuyao_session_wrapper.py`: wrapper for full context.

Suggested CLI modes:

```bash
liuyao-chart --lines "少阳 老阴 少阴 少阳 老阳 少阴" --question "问工作"
liuyao-chart --hexagram "离之大有" --question "问工作"
liuyao-chart --random --question "问工作"
```

## Error Handling

Errors should be explicit and user-correctable:

- Six-line input must contain exactly six results.
- Unknown line state names should list allowed states.
- Named hexagram input must identify a known original hexagram.
- If changed hexagram is supplied, it must be consistent with the derived moving lines.
- If line order is ambiguous, the tool must ask for bottom-to-top order instead of guessing.
- Missing eight-palace or najia rule entries should fail as implementation errors with the missing key.

## Tests

Add focused tests for:

- Manual six-line input parses bottom-to-top.
- `老阴` and `老阳` are moving and change polarity.
- Random generation produces six allowed line states and preserves them in JSON.
- `离之大有` parses as `离为火` changing to `火天大有` with moving line `[2]`.
- Inconsistent named hexagram and moving-line input raises a clear error.
- Hexagram JSON includes original, changed, and moving lines.
- Palace JSON includes palace, generation, shi, and ying.
- Najia JSON includes line stem-branch, branch, element, six relative, and role.
- Question context includes candidate useful gods but does not select final useful god.
- Liuyao JSON does not contain Bazi or Daliuren fields listed in the hard boundary.
- CLI and session wrappers output valid JSON.

## Migration And Future Work

After the MVP is stable, the next implementation stages can add:

- Six spirits.
- Month/day prosperity and decline checks.
- Month break, day clash, xunkong, and dynamic line checks.
- Flying and hidden spirit interactions.
- Useful-god final selection.
- Event timing.
- Time-based hexagram generation.
