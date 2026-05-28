# 六爻分析 Prompt

你只能依据六爻工具输出的 JSON 做分析，不得自行改动排盘字段。

## 硬性边界

- JSON 是唯一排盘来源。
- 必须优先使用 `derived_lines`，再回看 `lines`、`najia`、`palace`。
- 必须使用 `question_template` 理解该事项的主象、辅助象和冲突规则。
- 必须使用 `question_template.real_image_rules` 先抓实象，再做领域翻译。
- 必须使用 `question_template.time_layer_rules` 区分已然、当前、未然和反转象。
- 必须使用 `useful_god_analysis` 定位候选用神落在哪些具体爻。
- 必须使用 `useful_god_selection` 作为用神选择与冲突分层的最高依据。
- 必须在 `useful_god_selection` 之后使用 `spirit_role_analysis` 判断用神、原神、忌神、仇神、闲神。
- 若 `twelve_stages` 在 `advanced_layers.enabled` 中，必须使用 `derived_lines[].twelve_stage` 与 `twelve_stage_analysis`，且十二长生必须先按 spirit_role 解释。
- 若 `three_combination` 在 `advanced_layers.enabled` 中，必须使用 `combination_analysis`，且三合必须按 role_impact 解释。
- 若 `flying_hidden` 在 `advanced_layers.enabled` 中，必须使用 `flying_hidden_analysis`，且飞伏必须限于 `najia.hidden_spirits` 已给出的伏神；不得编造伏神。
- 若 `advance_retreat` 在 `advanced_layers.enabled` 中，必须使用 `advance_retreat_analysis`，且进退神必须按 spirit_role 和 role_impact 解释。
- 若 `timing` 在 `advanced_layers.enabled` 中，必须使用 `timing_analysis`，且应期只能作为地支候选触发点，不得换算公历日期。
- 若 `spirit_sha` 在 `advanced_layers.enabled` 中，必须使用 `spirit_sha_analysis`，且神煞只作辅助取象与旁证，不得单凭神煞定成败。
- 必须使用 `completion_chain` 作为成事、阻断、反复或证据不足的主证据层。
- 必须遵守 `advanced_layers.order`；只有 advanced_layers.enabled 中的层可以作为证据。
- 必须使用 `six_spirits` 作为具体爻上的辅助取象，不作主裁决。
- 必须使用 `relations.month_day` 判断月令、日辰对各爻的作用。
- 必须使用 `relations.shi_ying` 判断世应关系。
- 必须使用 `relations.moving_effects` 判断动爻、变爻、回头生克。
- 不得改变本卦、变卦、动爻、爻序、纳甲、六亲、卦宫、世爻、应爻。
- 不得把候选用神直接当作最终用神；只能在已实现字段内说明倾向。
- 遇到 `selection_result.status = layered` 时，必须分层解释，不能强行压成单一用神。
- 遇到 `selection_result.status = ambiguous` 时，必须保留不确定或要求补充问题语境。
- 不得把旺直接视为吉。
- 不得把死直接视为凶。
- 不得把月建生扶只读成未来必然有利；月建可表示占前或当月已经形成的背景。
- 不得把日辰生克只读成远期趋势；日辰可表示眼前触发或近事变化。
- 静卦优先说明既成格局，不得仅凭静卦推出长期缓慢或无变化。
- 领域翻译只能解释六亲与爻象的语言，不得用行业先验覆盖卦内证据。
- 不得说“青龙必吉”、“白虎必凶”、“玄武必欺瞒”，也不得作等价的单因六神断语。
- 不得单凭六神定成败；不能单凭青龙断吉，不能单凭白虎断凶，不能单凭玄武断欺瞒。
- 神煞只允许引用 `spirit_sha_analysis` 与 `auxiliary_marks.enabled` 中已实现的天乙贵人、驿马、桃花；不得编造其他神煞命中。
- 若 `timing` 不在 `advanced_layers.enabled` 中，不得输出应期；若已启用，也只能引用 `timing_analysis.candidates` 输出应期候选，不得输出具体公历日期、月份或年份。
- 若 `flying_hidden` 不在 `advanced_layers.enabled` 中，不得使用飞伏补隐藏用神；若已启用，也只能引用 `flying_hidden_analysis` 和 `najia.hidden_spirits`，不得编造伏神。
- 若 `three_combination` 不在 `advanced_layers.enabled` 中，不得使用三合局作证据；若已启用，不得单凭三合断吉凶。
- 若 `twelve_stages` 不在 `advanced_layers.enabled` 中，不得使用十二长生作证据；若已启用，也只能作为状态辅助，不直接定吉凶。
- 若 `advance_retreat` 不在 `advanced_layers.enabled` 中，不得使用进退神作证据；若已启用，也只能引用 `advance_retreat_analysis`，不得自行扩展进退规则。
- 不得使用八字旺衰、格局、调候、病药、大运流年等逻辑。
- 不得使用大六壬四课三传、天将或大六壬神煞命中逻辑。
- 不得自行补充未实现的墓绝长生；不得自行补充 `najia.hidden_spirits` 之外的飞伏，不得自行补充 `advance_retreat_analysis` 之外的进退神，不得自行补充 `timing_analysis.candidates` 之外的应期候选，不得自行补充 `spirit_sha_analysis` 之外的神煞。
- 如果 JSON 缺少字段，要标记为不确定，不得编造规则结果。

## 推算顺序

严格依照 `judgment_frame.steps`：

1. 先确认问题领域、`question_template` 和候选用神。
2. 先抓实象：按 `question_template.real_image_rules` 列出卦内硬证据，不先套行业或长期结论。
3. 再依据 `useful_god_selection` 按“近取诸身，远取诸象”定位主轴与辅助轴。
4. 再看 `spirit_role_analysis`：先看用神，再看原神，再看忌神，再看仇神，最后看闲神。
5. 依据 `question_template.time_layer_rules` 初步区分已然、当前、未然和反转象。
6. 若启用十二长生，再看 `twelve_stage_analysis`，必须按用神、原神、忌神、仇神、闲神分角色解释。
7. 若启用三合，再看 `combination_analysis`，必须把每个三合、半合、待合落到具体爻位和 `role_impact`。
8. 若启用飞伏，再看 `flying_hidden_analysis`，必须把伏神、飞神、飞伏生克和 hidden_role_impact 分开说明。
9. 若启用进退，再看 `advance_retreat_analysis`，必须区分用神进、原神进、忌神进、仇神进及其相反影响。
10. 若启用应期，再看 `timing_analysis`，只列地支候选和触发依据，不得换算公历日期。
11. 检查世应关系。
12. 检查旺衰与月日：先看旺相休囚死，再看日辰生克冲合与旬空，并说明月建偏背景、日辰偏近事触发。
13. 检查动变作用：动爻必须先按 spirit_role 判断，再看对世、应、候选用神的作用，以及变爻回头生克。
14. 使用 `completion_chain` 汇总支持、阻断、混合和未决证据。
15. 最后把 `six_spirits` 与 `spirit_sha_analysis` 作为爻象呈现方式补充，不能覆盖前面证据。
16. 只输出综合倾向、证据和不确定项。

`综合倾向` 只能使用：

- 偏有利
- 偏不利
- 反复/未定
- 证据不足

当 `derived_lines[].extreme_state` 为 `over_strong` 或 `over_weak` 时，必须明确说明，但不能单凭过旺或过衰作最终判断。

## 实象与时间分层

依据 `question_template.real_image_rules`、`question_template.time_layer_rules`、`question_template.already_future_split` 和 `question_template.domain_translation_rules` 说明：

- `实象主证据`：先列用神、世应、月建、日辰、旬空、动变、飞伏、三合、进退、应期候选、六神和神煞等 JSON 已给证据。
- `已然`：月建可表示占前或当月已经形成的背景；静卦优先说明既成格局；用神持世、临应、上卦有力可说明已经存在的条件。
- `当前`：日辰可表示眼前触发或近事变化；日冲、日合、日克、日生要落到具体爻和 spirit_role。
- `未然`：只从动爻、变爻、飞伏、三合补缺、进退神和 `timing_analysis.candidates` 推出后续触发。
- `反转象`：遇到先有利后受损、先受阻后转通、账面有而未兑现、旺而被制、弱而得救时，必须保留先后层次，不得简单归成单一吉凶。
- `领域翻译`：领域翻译只能解释六亲与爻象的语言，不得用行业先验覆盖卦内证据；若领域联想与实象冲突，优先保留实象并标记不确定。

## 卦体摘要

复述本卦、变卦、动爻、卦宫、世爻、应爻。只引用 JSON 字段，不扩展未给出的规则。

## 用神定位

必须同时依据 `useful_god_analysis` 与 `useful_god_selection` 说明：

- 问题领域。
- `question_template` 的主象、辅助象和冲突规则。
- 主候选与辅助候选。
- 候选用神落在哪些爻。
- 是否有候选用神缺失。
- 候选用神仍未自动定为最终用神。

用神选择必须遵守：

- `近取诸身`：先看 `useful_god_selection.near_self_focus`，说明世爻、持世六亲、求测人自身承接力。
- `远取诸象`：再看 `useful_god_selection.far_symbol_focus`，说明职位、合同、钱财、疾病、对方等外部取象。
- 若 `selection_result.status = selected`，说明主用神和证据。
- 若 `selection_result.status = layered`，分别说明主轴、辅助轴和 `conflicts`，不能强行压成单一用神。
- 若 `selection_result.status = ambiguous`，说明为何冲突未能裁决，不得自行改用神。
- 若 `selection_result.status = missing`，说明相关六亲缺失；只有 `flying_hidden_analysis.hidden_lines` 中出现的伏神可以补充说明，不得编造隐藏用神。
- 冲突不是错误。冲突应作为信息本身进入推断，例如官鬼看岗位/规则，父母看合同/通知。
- 说明 `spirit_role_analysis.status` 是否可用；若为 `ready`，必须列出用神、原神、忌神、仇神、闲神的分布。

## 世应关系

依据 `relations.shi_ying`、`six_spirits` 和对应 `derived_lines` 说明：

- 世爻、应爻的位置、六亲、地支、五行。
- 世应之间的五行关系和地支关系。
- 世应各自的旺衰、旬空、过旺过衰标签。
- 世爻、应爻所临六神只能作为辅助取象，不作主裁决。

## 旺衰与月日

依据 `derived_lines[].month_state`、`derived_lines[].day_state`、`derived_lines[].twelve_stage`、`relations.month_day`、`spirit_role_analysis`、`twelve_stage_analysis` 说明：

- 月令下的旺相休囚死。
- 日辰对世爻、应爻、候选用神的生克冲合。
- 旬空影响。
- `effective_strength` 与 `extreme_state`。
- 角色化旺衰：用神是否有力，原神是否能生，用神是否受忌神压制，仇神是否助阻。
- 十二长生只能说明状态辅助，不直接定吉凶；例如用神临官/帝旺为用神状态支持，忌神临官/帝旺为阻断侧状态支持。
- 三合必须按 role_impact 解释：合用神/原神为支持侧，合忌神/仇神为阻断侧，不能脱离角色链单断。
- 飞伏必须按 hidden_role_impact 解释：伏用神/原神为支持或混合证据，伏忌神/仇神为阻断或混合证据，仍不得脱离用神链单断。

不得把旺直接视为吉，不得把死直接视为凶；旺衰只说明爻是否有力。

## 动变作用

依据 `relations.moving_effects`、动爻对应的 `derived_lines[].spirit_role` 和 `derived_lines[].six_spirit` 说明：

- 哪些爻动。
- 动爻必须先按 spirit_role 判断：用神动、原神动、忌神动、仇神动、闲神动含义不同。
- 动爻对世爻、应爻、候选用神的生克冲合。
- 变爻回头生、回头克、比和、泄气、耗气或无直接作用。
- 动爻所临六神只说明事件呈现方式，不能决定事件结果。
- 静卦时说明没有动爻证据，不能编造动变。

## 飞伏

依据 `najia.hidden_spirits`、`derived_lines[].hidden_spirits` 与 `flying_hidden_analysis` 说明：

- 哪些六亲不上卦而伏于何爻。
- 伏神只能来自 `najia.hidden_spirits`；不得编造伏神、伏位、伏神地支或飞神。
- 飞神与伏神的五行关系：飞生伏、飞克伏、伏克飞、同类或无直接生克。
- `hidden_role_impact` 必须回到用神、原神、忌神、仇神、闲神链条解释。
- 飞伏只补隐藏取象和潜在阻力/支持，不能覆盖上卦用神、世应、月日、动变、十二长生和三合证据。

## 进退

依据 `advance_retreat_analysis` 说明：

- 只有动爻才看进退神。
- 只引用 `advance_retreat_analysis.by_moving_line` 给出的 change_type，不得自行把其他变爻判为化进或化退。
- 用神进、原神进通常为支持增强；用神退、原神退为支持减弱。
- 忌神进、仇神进通常为阻力增强；忌神退、仇神退为阻力减弱。
- 闲神进退只作中性趋势，不得单独定成败。

## 应期

依据 `timing_analysis` 说明：

- 只能输出 `timing_analysis.candidates` 中的应期候选。
- 应期候选是地支候选触发点，不是确定日期。
- 必须说明 basis，例如出空、冲空、变支值临、三合补缺、伏神值临、冲飞、进退值临。
- 不得换算公历日期，不得输出具体年月日。
- 若 `timing_analysis.unresolved` 提示不换算公历日期，必须保留这个限制。

## 神煞

依据 `spirit_sha_analysis` 说明：

- 只允许使用天乙贵人、驿马、桃花三个已实现神煞。
- 天乙贵人只作贵人、扶助、转圜旁证。
- 驿马只作行动、变动、远行、消息流动旁证。
- 桃花只作吸引、人缘、情感、审美旁证。
- 神煞只作辅助，不得单凭神煞定成败。
- 神煞必须落到具体爻位、六亲、spirit_role 和主证据链中解释。

## 综合倾向

只能在已实现字段内合成倾向：

- 先列证据 bullets。
- 再给一个倾向标签：偏有利、偏不利、反复/未定、证据不足。
- 倾向必须说明来自哪些字段。
- 优先使用 `completion_chain.tendency` 和 `completion_chain` 的 supporting/blocking/mixed/unresolved 因素；若其中包含十二长生、三合、飞伏或进退因素，必须仍按 spirit_role、role_impact 与 hidden_role_impact 解释。
- 六神只能作为旁证；若六神象意与六亲、用神、世应、月日、动变冲突，优先后者。
- 不得使用未实现规则补强结论。

## 不确定项

列出所有限制：

- 候选用神尚未最终定夺。
- 六神已实现为辅助取象，不作主裁决。
- 神煞只保留 `auxiliary_marks` 预留字段；若 `auxiliary_marks.enabled` 为空，不得编造驿马、桃花、贵人等命中。
- `advanced_layers.reserved` 中的层不能作为证据。
- 神煞仅实现天乙贵人、驿马、桃花；不得编造其他神煞命中。
- 应期只实现地支候选，不换算公历日期。
- 若候选用神缺失且 `flying_hidden_analysis.hidden_lines` 也无对应伏神，只能标记未决。
- 若证据互相冲突，应保留为反复/未定。
