# Liuyao Question Templates and Six-Spirit Imagery Design

## Goal

Extend Liuyao v3 into a v4 framework that improves imagery quality through:

1. Question-specific templates.
2. Six-spirit auxiliary imagery.
3. Prompt constraints that keep the final reasoning anchored in Liuyao-native chart evidence.

This stage is for better image selection and narrative precision. It is not a full auspicious/inauspicious judgment engine.

## Hard Boundary

This remains Liuyao-only.

Forbidden:

- Bazi day-master strength, ten-god imagery, pattern, climate, remedy, luck, or discipline fields.
- Daliuren four lessons, transmissions, heavenly officers, or Daliuren spirit-sha logic.
- Treating six spirits or spirit-sha as final judgment authority.
- Free-form model invention of unsupported Liuyao rules.

This stage does not implement:

- Original spirit / avoiding spirit / enemy spirit power framework.
- Flying and hidden spirits.
- Three-combination bureau judgment.
- Tomb, absolute, long-life cycle details.
- Advance and retreat spirit.
- Event timing.
- Final deterministic good/bad judgment.

## Schema Version

Upgrade:

```json
"schema": "liuyao_chart_v4"
```

Keep v3 fields stable. Add:

```json
{
  "question_template": {},
  "six_spirits": {},
  "auxiliary_marks": {}
}
```

`imagery_context` and `useful_god_selection` remain the primary imagery-selection layer. `question_template` gives the selection layer a domain-specific contract. `six_spirits` adds auxiliary texture attached to concrete lines.

## Question Templates

Add a deterministic template dictionary. The template is selected from the existing `question_context.domain` and question tokens. If multiple templates match, keep the one matching `question_context.domain`; preserve other matches as `secondary_templates`.

Initial templates:

```json
{
  "事业/工作": {
    "template_id": "career_work",
    "main_images": [
      {
        "six_relative": "官鬼",
        "image": "职位/岗位/规则/上级",
        "reason": "求职、工作、offer 以官鬼为职位和规则主象。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "父母",
        "image": "合同/通知/单位文书",
        "reason": "入职、offer、合同、通知等流程载体取父母。"
      },
      {
        "six_relative": "妻财",
        "image": "薪资/收益/现实利益",
        "reason": "薪资待遇和现实收益取妻财。"
      },
      {
        "six_relative": "兄弟",
        "image": "竞争者/同事/消耗",
        "reason": "竞争、同事、分利和阻力可看兄弟。"
      }
    ],
    "conflict_rules": [
      "工作 + 合同：官鬼为岗位主轴，父母为文书流程辅助轴。",
      "工作 + 薪资：官鬼为岗位主轴，妻财为薪资收益辅助轴。",
      "工作 + 竞争：官鬼为岗位主轴，兄弟为竞争阻力辅助轴。"
    ]
  },
  "财运/交易": {
    "template_id": "wealth_trade",
    "main_images": [
      {
        "six_relative": "妻财",
        "image": "钱财/货物/收入/客户资源",
        "reason": "求财、交易、收款以妻财为财物主象。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "子孙",
        "image": "客源/产出/解决方案",
        "reason": "生财之路、产品产出、客户流量可取子孙。"
      },
      {
        "six_relative": "兄弟",
        "image": "竞争/分财/成本消耗",
        "reason": "分财、竞争、成本消耗可取兄弟。"
      },
      {
        "six_relative": "父母",
        "image": "合同/票据/手续",
        "reason": "交易合同、票据、手续取父母。"
      }
    ],
    "conflict_rules": [
      "钱财 + 合同：妻财为财物主轴，父母为手续辅助轴。",
      "钱财 + 竞争：妻财为财物主轴，兄弟为分财阻力。",
      "钱财 + 客户：妻财为收益主轴，子孙为客源或产出辅助轴。"
    ]
  },
  "感情/婚恋": {
    "template_id": "relationship",
    "main_images": [
      {
        "six_relative": "妻财",
        "image": "女方/妻子/现实吸引",
        "reason": "男问感情多以妻财为对象主象。"
      },
      {
        "six_relative": "官鬼",
        "image": "男方/丈夫/关系约束",
        "reason": "女问感情多以官鬼为对象主象。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "世应",
        "image": "双方关系",
        "reason": "关系互动必须合看世应。"
      },
      {
        "six_relative": "兄弟",
        "image": "竞争者/朋友干扰",
        "reason": "竞争者、同辈干扰、分夺可看兄弟。"
      },
      {
        "six_relative": "父母",
        "image": "婚书/家长/现实条件",
        "reason": "婚书、家长、房屋、现实制度条件可看父母。"
      }
    ],
    "conflict_rules": [
      "感情对象不明时，不强行按性别定单一用神；保留世应互动和对象六亲两层。",
      "对象 + 家长/婚书：对象六亲为主轴，父母为现实条件辅助轴。"
    ]
  },
  "考试/学业": {
    "template_id": "exam_study",
    "main_images": [
      {
        "six_relative": "父母",
        "image": "试卷/证书/录取文书/学习材料",
        "reason": "考试、证书、录取、申请材料以父母为主象。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "官鬼",
        "image": "排名/规则/压力/录取约束",
        "reason": "考试规则、压力、名次和录取约束可看官鬼。"
      },
      {
        "six_relative": "子孙",
        "image": "发挥/表达/解题输出",
        "reason": "考试发挥、表达输出、解题思路可看子孙。"
      }
    ],
    "conflict_rules": [
      "考试 + 证书：父母为文书主轴。",
      "考试 + 发挥：父母为考试载体主轴，子孙为发挥辅助轴。",
      "考试 + 压力/规则：父母为文书主轴，官鬼为规则压力辅助轴。"
    ]
  },
  "健康/疾病": {
    "template_id": "health_illness",
    "main_images": [
      {
        "six_relative": "官鬼",
        "image": "疾病/病因/压力源",
        "reason": "疾病、病症、压力源以官鬼为病象主轴。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "子孙",
        "image": "药物/治疗方案/恢复力",
        "reason": "药物、治疗、缓解和恢复方案取子孙。"
      },
      {
        "six_relative": "父母",
        "image": "医院/检查报告/病历",
        "reason": "医院、检查报告、病历文书取父母。"
      }
    ],
    "conflict_rules": [
      "疾病 + 治疗：官鬼为病象主轴，子孙为药物治疗辅助轴。",
      "疾病 + 报告：官鬼为病象主轴，父母为检查文书辅助轴。"
    ]
  },
  "失物/寻找": {
    "template_id": "lost_found",
    "main_images": [
      {
        "six_relative": "妻财",
        "image": "财物/普通物品",
        "reason": "普通财物、贵重物品多以妻财为主象。"
      },
      {
        "six_relative": "父母",
        "image": "证件/文书/衣物/房屋内物件",
        "reason": "证件、文书、衣物、资料类物品可取父母。"
      },
      {
        "six_relative": "子孙",
        "image": "小物件/玩具/宠物相关物",
        "reason": "玩具、小物件、子女相关物可取子孙。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "世应",
        "image": "自己与外部位置",
        "reason": "失物需合看世应代表内外、自他和找寻关系。"
      }
    ],
    "conflict_rules": [
      "失物物类不明时，不能强行定单一用神；保留物类候选。",
      "证件类优先父母，钱财类优先妻财，玩具小物类可取子孙。"
    ]
  },
  "诉讼/纠纷": {
    "template_id": "dispute_lawsuit",
    "main_images": [
      {
        "six_relative": "官鬼",
        "image": "官非/规则/压力/处罚",
        "reason": "诉讼、纠纷、处罚和规则压力以官鬼为主象。"
      }
    ],
    "auxiliary_images": [
      {
        "six_relative": "父母",
        "image": "文书/证据/判书/合同",
        "reason": "证据、合同、文书、判书取父母。"
      },
      {
        "six_relative": "兄弟",
        "image": "对立方/竞争方/牵连者",
        "reason": "对立竞争、牵连、同辈争夺可看兄弟。"
      },
      {
        "six_relative": "妻财",
        "image": "赔偿/钱财争议",
        "reason": "赔偿、罚款、财产争议取妻财。"
      }
    ],
    "conflict_rules": [
      "纠纷 + 合同证据：官鬼为压力规则主轴，父母为证据文书辅助轴。",
      "纠纷 + 赔偿：官鬼为规则主轴，妻财为赔偿财物辅助轴。"
    ]
  }
}
```

### `question_template` Output

Example:

```json
{
  "template_id": "career_work",
  "domain": "事业/工作",
  "selected_by": ["question_context.domain", "question_tokens"],
  "main_images": [],
  "auxiliary_images": [],
  "conflict_rules": [],
  "secondary_templates": [],
  "must_not_mix": [
    "模板只决定取象入口，不决定最终成败。",
    "模板不能覆盖 useful_god_selection 的分层结果。",
    "模板不能引入八字或大六壬逻辑。"
  ]
}
```

## Template Integration

Template data should influence `imagery_context` and `useful_god_selection` in a bounded way:

- If the template main image matches an existing candidate useful god, mark it as `template_main`.
- If the template auxiliary image matches a token or candidate, mark it as `template_auxiliary`.
- If the same question hits more than one image in the template, preserve it as a layered conflict.
- If the template suggests an image absent from the chart, record it as missing; do not invent hidden spirits.
- If the existing v3 imagery token layer conflicts with the template, keep both and mark the result `ambiguous` unless the template has a clear main image for the domain.

## Six Spirits

Add six-spirit assignment by day stem.

Order:

```json
["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
```

Starting spirit by day stem:

```json
{
  "甲": "青龙",
  "乙": "青龙",
  "丙": "朱雀",
  "丁": "朱雀",
  "戊": "勾陈",
  "己": "螣蛇",
  "庚": "白虎",
  "辛": "白虎",
  "壬": "玄武",
  "癸": "玄武"
}
```

Assign from the initial line upward, advancing one spirit per line through the fixed order.

Example: 壬日 starts at 玄武 on 初爻, then 青龙, 朱雀, 勾陈, 螣蛇, 白虎.

### Six-Spirit Imagery

Use a conservative dictionary:

```json
{
  "青龙": {
    "imagery": ["喜庆", "财喜", "文雅", "顺遂"],
    "cautions": ["不能单凭青龙断吉"]
  },
  "朱雀": {
    "imagery": ["口舌", "消息", "文书", "表达"],
    "cautions": ["需依附具体爻和六亲，不得单独断口舌"]
  },
  "勾陈": {
    "imagery": ["迟滞", "田土", "牵连", "旧事"],
    "cautions": ["不能单凭勾陈断拖延，需合看动静和月日"]
  },
  "螣蛇": {
    "imagery": ["虚惊", "疑虑", "缠绕", "怪异"],
    "cautions": ["不能单凭螣蛇断异常或欺诈"]
  },
  "白虎": {
    "imagery": ["伤病", "压力", "冲突", "急迫"],
    "cautions": ["不能单凭白虎断凶"]
  },
  "玄武": {
    "imagery": ["隐情", "暗昧", "欺瞒", "私下"],
    "cautions": ["不能单凭玄武断欺瞒"]
  }
}
```

### `six_spirits` Output

```json
{
  "start_basis": "按日干起六神",
  "day_stem": "壬",
  "start_spirit": "玄武",
  "scope": "辅助取象，不作主裁决",
  "lines": [
    {
      "position": 1,
      "spirit": "玄武",
      "imagery": ["隐情", "暗昧", "欺瞒", "私下"],
      "attached_to": {
        "six_relative": "父母",
        "role": null,
        "is_shi": false,
        "is_ying": false,
        "is_candidate_useful_god": true,
        "moving": false
      },
      "interpretation_scope": [
        "只用于说明该爻象意呈现方式。",
        "必须依附六亲、世应、用神、动变、旺衰字段使用。"
      ],
      "cautions": ["不能单凭玄武断欺瞒"]
    }
  ]
}
```

Six spirits must also be copied onto `derived_lines[].six_spirit` for easy prompt use.

## Auxiliary Marks

Do not implement spirit-sha calculation in this stage.

Add a reserved top-level field:

```json
{
  "auxiliary_marks": {
    "enabled": [],
    "reserved": ["驿马", "桃花", "贵人"],
    "scope": "预留字段；当前不计算神煞，不得在 prompt 中编造命中。"
  }
}
```

This prevents the prompt from fabricating spirit-sha while preserving a future schema location.

## Prompt Upgrade

Update `liuyao_prompt.md`.

Required constraints:

- Use `question_template` to understand the question-specific imagery entry.
- Use `six_spirits` only as auxiliary imagery attached to concrete lines.
- Six spirits cannot override:
  - useful-god selection
  - six relatives
  - shi/ying
  - month/day strength
  - moving and changed-line effects
- Do not say "青龙必吉", "白虎必凶", "玄武必欺瞒", or equivalent deterministic claims.
- If six-spirit imagery conflicts with six-relative or useful-god evidence, prefer six-relative/useful-god/shi-ying/month-day/moving evidence and mark six spirit as a side note.
- If `auxiliary_marks.enabled` is empty, state that spirit-sha is not implemented when relevant; do not invent hits.

Prompt section changes:

- `用神定位`: include template main/auxiliary images.
- `世应关系`: include six spirits on shi and ying as auxiliary imagery.
- `旺衰与月日`: no direct six-spirit effect on strength.
- `动变作用`: if a moving line has a six spirit, describe it as the moving event's presentation style, not as the event's outcome.
- `综合倾向`: six spirits may appear only as supporting side evidence, not primary conclusion evidence.
- `不确定项`: mention that spirit-sha remains reserved and unimplemented.

## Tests

Add tests for:

1. Career template selection:
   - question: `问工作 offer 合同什么时候下来`
   - domain: `事业/工作`
   - expect `question_template.template_id == "career_work"`
   - expect main image `官鬼`
   - expect auxiliary image `父母`

2. Template integration with layered imagery:
   - same question
   - expect useful-god selection remains `layered`
   - expect main useful god remains `官鬼`
   - expect auxiliary useful god includes `父母`

3. Six-spirit assignment:
   - day stem `壬`
   - expect initial line spirit `玄武`
   - expect line order: `玄武`, `青龙`, `朱雀`, `勾陈`, `螣蛇`, `白虎`

4. Six spirits attach to derived lines:
   - every `derived_lines[]` has `six_spirit`
   - `six_spirits.lines[]` includes attached six-relative and role fields

5. Prompt policy:
   - prompt requires `question_template`
   - prompt requires `six_spirits`
   - prompt includes "辅助取象，不作主裁决"
   - prompt forbids single-factor six-spirit judgment
   - prompt states spirit-sha is reserved when `auxiliary_marks.enabled` is empty

6. Boundary:
   - v4 JSON contains no Bazi or Daliuren fields.
   - `auxiliary_marks.enabled` is empty.
   - prompt does not authorize unimplemented spirit-sha.

## Acceptance Criteria

- `liuyao_chart_v4` is emitted by the Liuyao chart tool.
- Existing v3 fields remain present and compatible.
- Question templates improve imagery selection without replacing useful-god selection.
- Six spirits are assigned deterministically from day stem.
- Six-spirit imagery is always attached to concrete lines.
- Spirit-sha is reserved but not calculated.
- Prompt prevents six spirits or spirit-sha from becoming unsupported final judgment logic.
- Full Liuyao tests and full project tests pass.
