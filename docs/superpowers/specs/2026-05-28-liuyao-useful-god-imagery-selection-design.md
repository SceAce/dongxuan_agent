# Liuyao Useful-God Imagery Selection Design

## Goal

Extend Liuyao v2 into a v3 useful-god selection framework based on imagery.

The purpose is not to force a single useful god. When imagery conflicts, the conflict should become part of the judgment evidence. The principle is:

> 近取诸身，远取诸象。

In implementation terms:

- Near-self evidence describes the querent, immediate involvement, shi line, self-side pressure, and whether the querent can bear or receive the matter.
- Far-symbol evidence describes the external object, counterpart, institution, document, money, disease, offer, rule, or event carrier.
- Conflicting imagery should be preserved as layered axes instead of being flattened into one candidate.

## Hard Boundary

This remains Liuyao-only.

Forbidden:

- Bazi day-master strength, ten-god imagery, pattern, climate, remedy, luck, or discipline fields.
- Daliuren four lessons, transmissions, heavenly officers, or Daliuren spirit-sha logic.
- Free-form model selection of useful gods outside JSON fields.

Allowed:

- Local Liuyao imagery rules derived from the local knowledge base.
- Existing Liuyao fields: six relatives, shi/ying, useful-god candidates, derived lines, month/day state, moving effects.

## Knowledge Basis

Use local knowledge only. Do not browse the web.

Relevant local sources already identified:

- `/home/source/Documents/东玄知识库/wiki/topics/六爻.md`
- `/home/source/Documents/东玄知识库/wiki/entities/用神.md`
- `/home/source/Documents/东玄知识库/wiki/sources/六爻分类占验技法王虎应-_王虎应_-_Z-Library-558e742f.md`
- `/home/source/Documents/东玄知识库/wiki/sources/六爻初级知识入门-dfc33e86.md`
- `/home/source/Documents/东玄知识库/wiki/sources/六爻古籍合集：[增删卜易][卜筮正宗][卜筮大全][易林补遗][易冒][易隐][火珠林](1)-a46fb993.md`

The local corpus supports:

- Usefulness of question-specific useful-god selection.
- Six relatives as imagery carriers.
- Need to extract information by question category, six-relative class, line position, and other chart structures.

## Schema Version

Upgrade:

```json
"schema": "liuyao_chart_v3"
```

Keep all v2 fields stable. Add:

```json
{
  "imagery_context": {},
  "useful_god_selection": {}
}
```

## Imagery Dictionary

Add a structured dictionary module for six-relative imagery.

Initial v3 dictionary:

```json
{
  "官鬼": {
    "near_self": ["压力", "忧虑", "约束", "责任", "风险"],
    "far_symbol": ["职位", "规则", "上级", "疾病", "官非", "丈夫/男方"],
    "domains": ["事业/工作", "健康/疾病", "感情/婚恋", "诉讼/纠纷"]
  },
  "父母": {
    "near_self": ["保护", "承载", "学习负担", "信息接收"],
    "far_symbol": ["文书", "合同", "证书", "房屋", "单位", "长辈", "消息"],
    "domains": ["文书/合同", "考试/学业", "事业/工作", "家宅/房屋"]
  },
  "妻财": {
    "near_self": ["资源", "欲望", "收益目标", "现实利益"],
    "far_symbol": ["钱财", "货物", "客户资源", "女方/妻子", "收入"],
    "domains": ["财运/交易", "感情/婚恋", "事业/工作"]
  },
  "子孙": {
    "near_self": ["放松", "产出", "解决方案", "表达", "享乐"],
    "far_symbol": ["药物", "治疗方案", "作品", "客户流量", "子女", "下属"],
    "domains": ["健康/疾病", "财运/交易", "考试/学业", "创作/产出"]
  },
  "兄弟": {
    "near_self": ["同辈", "自我消耗", "竞争心", "分担"],
    "far_symbol": ["竞争者", "合伙人", "同事", "分财者", "阻力"],
    "domains": ["财运/交易", "事业/工作", "合作/竞争"]
  }
}
```

This dictionary is a selection aid, not a final judgment.

## `imagery_context`

Add a question parsing and imagery match layer:

```json
{
  "question": "问工作 offer 合同什么时候下来",
  "tokens": ["工作", "offer", "合同"],
  "domain": "事业/工作",
  "matches": [
    {
      "token": "工作",
      "six_relative": "官鬼",
      "layer": "far_symbol",
      "image": "职位",
      "reason": "工作职位与官鬼取象相符"
    },
    {
      "token": "合同",
      "six_relative": "父母",
      "layer": "far_symbol",
      "image": "合同",
      "reason": "合同文书与父母取象相符"
    }
  ],
  "near_self_principle": "近取诸身：先看世爻、持世六亲、作用到世爻的候选。",
  "far_symbol_principle": "远取诸象：外部对象、文书、职位、钱财、对方等按六亲取象分层。"
}
```

Rules:

- Keep token extraction simple and deterministic.
- A token can map to more than one six-relative image.
- Do not call an LLM inside the tool to parse tokens.
- If no token matches, keep `matches` empty and rely on existing domain candidates.

## `useful_god_selection`

Add a selection framework:

```json
{
  "principle": "近取诸身，远取诸象",
  "mode": "imagery_guided",
  "near_self_focus": [
    {
      "position": 6,
      "name": "上爻",
      "six_relative": "兄弟",
      "role": "世",
      "reason": "世爻代表求测人自身与承接能力",
      "strength": "very_strong",
      "cautions": ["旬空"]
    }
  ],
  "far_symbol_focus": [
    {
      "six_relative": "官鬼",
      "image": "职位",
      "matching_lines": [3],
      "reason": "工作职位以官鬼为象"
    },
    {
      "six_relative": "父母",
      "image": "合同",
      "matching_lines": [1],
      "reason": "合同文书以父母为象"
    }
  ],
  "conflicts": [
    {
      "type": "layered_imagery",
      "summary": "工作 offer 同时涉及职位与合同",
      "candidates": ["官鬼", "父母"],
      "near_self_question": "世爻能否承接职位与流程压力",
      "far_symbol_question": "职位机会与合同文书是否同步成事",
      "interpretation_hint": "不能简单二选一；官鬼看岗位/规则，父母看文书/通知。"
    }
  ],
  "primary_axis": [
    {
      "axis": "self_to_main_symbol",
      "near": "世爻",
      "far": "官鬼",
      "reason": "问我能否得到工作，先看世爻与职位象"
    }
  ],
  "secondary_axes": [
    {
      "axis": "document_flow",
      "near": "世爻",
      "far": "父母",
      "reason": "offer 合同落地需看文书通知"
    }
  ],
  "selection_result": {
    "status": "layered",
    "main_useful_god": "官鬼",
    "auxiliary_useful_gods": ["父母"],
    "watch_relatives": ["兄弟"],
    "conflict_reading": [
      "官鬼与父母不是互斥；前者看岗位机会，后者看文书流程。",
      "若官鬼有力而父母受克，可读为岗位有机会但手续/通知受阻。"
    ]
  }
}
```

### Status Values

- `selected`: one useful god dominates and no meaningful conflict exists.
- `layered`: multiple useful gods describe different layers of the same matter.
- `ambiguous`: evidence is insufficient or the question wording maps to competing images without chart support.
- `missing`: the relevant six-relative image is absent and hidden spirits are not implemented.

### Conflict Rules

Do not treat conflict as an error.

Conflict should be generated when:

- Two or more imagery matches are relevant to the question.
- A near-self line and far-symbol line point in different directions.
- The same question contains both a thing and its document/procedure, such as work + contract.
- The same question contains person + money, such as partner + debt.
- The same question contains disease + medicine, such as illness + treatment.

Conflict should include:

- `summary`
- candidate relatives
- why each candidate is valid
- what the near-self layer asks
- what the far-symbol layer asks
- how the prompt should interpret the layered meaning

## Prompt Upgrade

Update `liuyao_prompt.md`:

- Require `useful_god_selection` as the authority for useful-god choice.
- Explain `近取诸身，远取诸象`.
- In `用神定位`, separate:
  - near-self focus
  - far-symbol focus
  - conflicts
  - primary axis
  - secondary axes
- Do not resolve `layered` or `ambiguous` into a single useful god.
- If `selection_result.status = layered`, explain each layer.
- If `selection_result.status = ambiguous`, ask for clarification or mark uncertainty.
- If `selection_result.status = missing`, do not invent hidden spirits.

## Tests

Add focused tests for:

- Question with `工作 offer 合同` creates imagery matches for `官鬼` and `父母`.
- `useful_god_selection.principle` equals `近取诸身，远取诸象`.
- Work-contract question produces `status = layered`.
- Work-contract question sets `main_useful_god = 官鬼` and auxiliary `父母`.
- Near-self focus includes the shi line.
- Far-symbol focus includes concrete matching lines for useful-god relatives.
- Conflict contains the hint that 官鬼 and 父母 are not mutually exclusive.
- Prompt mentions `useful_god_selection`, `近取诸身`, `远取诸象`, `layered`, and `ambiguous`.

## Non-Goals

This stage does not implement:

- Full natural-language semantic parsing.
- Hidden spirits.
- Six spirits.
- Final useful-god certainty in all questions.
- Event timing.
- Domain-specific full judgment templates.

## Acceptance Criteria

- `liuyao-chart --hexagram "离之大有" --question "问工作 offer 合同什么时候下来" --format json` outputs `schema = liuyao_chart_v3`.
- Output contains `imagery_context` and `useful_god_selection`.
- The work-offer-contract case is `layered`, not forced into one useful god.
- Prompt requires using `useful_god_selection` and preserves layered conflicts.
- Full test suite passes.
