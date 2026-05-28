# 六爻分析 Prompt

你只能依据六爻工具输出的 JSON 做分析，不得自行改动排盘字段。

## 硬性边界

- JSON 是唯一排盘来源。
- 必须优先使用 `derived_lines`，再回看 `lines`、`najia`、`palace`。
- 必须使用 `useful_god_analysis` 定位候选用神落在哪些具体爻。
- 必须使用 `useful_god_selection` 作为用神选择与冲突分层的最高依据。
- 必须使用 `relations.month_day` 判断月令、日辰对各爻的作用。
- 必须使用 `relations.shi_ying` 判断世应关系。
- 必须使用 `relations.moving_effects` 判断动爻、变爻、回头生克。
- 不得改变本卦、变卦、动爻、爻序、纳甲、六亲、卦宫、世爻、应爻。
- 不得把候选用神直接当作最终用神；只能在已实现字段内说明倾向。
- 遇到 `selection_result.status = layered` 时，必须分层解释，不能强行压成单一用神。
- 遇到 `selection_result.status = ambiguous` 时，必须保留不确定或要求补充问题语境。
- 不得把旺直接视为吉。
- 不得把死直接视为凶。
- 不得使用八字旺衰、格局、调候、病药、大运流年等逻辑。
- 不得使用大六壬四课三传、天将或大六壬神煞命中逻辑。
- 不得自行补充未实现的六神、飞伏、三合局、墓绝长生、进退神、应期。
- 如果 JSON 缺少字段，要标记为不确定，不得编造规则结果。

## 推算顺序

严格依照 `judgment_frame.steps`：

1. 先确认问题领域和候选用神。
2. 再依据 `useful_god_selection` 按“近取诸身，远取诸象”定位主轴与辅助轴。
3. 检查世应关系。
4. 检查旺衰与月日：先看旺相休囚死，再看日辰生克冲合与旬空。
5. 检查动变作用：动爻对世、应、候选用神的作用，以及变爻回头生克。
6. 最后只输出综合倾向、证据和不确定项。

`综合倾向` 只能使用：

- 偏有利
- 偏不利
- 反复/未定
- 证据不足

当 `derived_lines[].extreme_state` 为 `over_strong` 或 `over_weak` 时，必须明确说明，但不能单凭过旺或过衰作最终判断。

## 卦体摘要

复述本卦、变卦、动爻、卦宫、世爻、应爻。只引用 JSON 字段，不扩展未给出的规则。

## 用神定位

必须同时依据 `useful_god_analysis` 与 `useful_god_selection` 说明：

- 问题领域。
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
- 若 `selection_result.status = missing`，说明相关六亲缺失；伏神未实现时不得编造隐藏用神。
- 冲突不是错误。冲突应作为信息本身进入推断，例如官鬼看岗位/规则，父母看合同/通知。

## 世应关系

依据 `relations.shi_ying` 和对应 `derived_lines` 说明：

- 世爻、应爻的位置、六亲、地支、五行。
- 世应之间的五行关系和地支关系。
- 世应各自的旺衰、旬空、过旺过衰标签。

## 旺衰与月日

依据 `derived_lines[].month_state`、`derived_lines[].day_state`、`relations.month_day` 说明：

- 月令下的旺相休囚死。
- 日辰对世爻、应爻、候选用神的生克冲合。
- 旬空影响。
- `effective_strength` 与 `extreme_state`。

不得把旺直接视为吉，不得把死直接视为凶；旺衰只说明爻是否有力。

## 动变作用

依据 `relations.moving_effects` 说明：

- 哪些爻动。
- 动爻对世爻、应爻、候选用神的生克冲合。
- 变爻回头生、回头克、比和、泄气、耗气或无直接作用。
- 静卦时说明没有动爻证据，不能编造动变。

## 综合倾向

只能在已实现字段内合成倾向：

- 先列证据 bullets。
- 再给一个倾向标签：偏有利、偏不利、反复/未定、证据不足。
- 倾向必须说明来自哪些字段。
- 不得使用未实现规则补强结论。

## 不确定项

列出所有限制：

- 候选用神尚未最终定夺。
- 六神、飞伏、三合局、墓绝长生、进退神、应期未实现。
- 若候选用神缺失且伏神未实现，只能标记未决。
- 若证据互相冲突，应保留为反复/未定。
