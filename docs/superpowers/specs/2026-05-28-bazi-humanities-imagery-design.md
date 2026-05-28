# Bazi Humanities And Cross-Discipline Imagery Design

## Goal

Improve Bazi imagery for humanities, social sciences, and cross-discipline major or career questions.

The local tool must not guess precise modern majors or careers directly. It should constrain the model by producing evidence-backed symbolic structure:

1. Natal structure, strength, pattern, remedy, branch relations, luck and year triggers.
2. Middle images such as text expression, institutional reasoning, research specialization, information processing, engineering systems, education training, communication, resource management, arts/design, and health/life-science training.
3. Spirit-sha auxiliary evidence that only adjusts middle-image confidence.
4. A multi-dimensional discipline profile that identifies strong discipline groups and cross-domain combinations.
5. Explicit constraints for the model when it uses web search or general knowledge to map those groups to modern majors or careers.

The design replaces a hard humanities-versus-STEM split with discipline group scoring. Cross-domain outcomes are first-class results, not fallback cases.

## Current Context

`dongxuan_agent/bazi/imagery.py` already builds `imagery_analysis`, including:

- `candidate_images`, `main_image`, `secondary_image`
- `answer_guidance.major_or_career_identification`
- `symbolic_layers`, loaded from `/home/source/Documents/东玄知识库/wiki/structured/bazi_symbolic_layers.json`
- `landing_evidence`, which currently evaluates modern landing rules such as software engineering, law, education, Chinese language and literature, and communication studies

The current implementation has two weaknesses:

- Humanities images exist, but they are thin and often appear only as weakened or excluded modern landing rules.
- The decision layer is still oriented toward modern major names instead of a stable symbolic discipline profile.

The Daliuren side already has a mature rule boundary for spirit-sha: spirit-sha is auxiliary, must hit key positions, and must not replace structural judgment. Bazi should adopt that principle, but use Bazi-specific spirit-sha rules rather than reusing Daliuren four-lessons/transmissions logic.

## Non-Goals

- Do not build a full exhaustive Bazi spirit-sha encyclopedia in the first pass.
- Do not let spirit-sha decide a major or career by itself.
- Do not force every result into humanities or STEM.
- Do not output large candidate lists of majors.
- Do not let web search override local chart evidence.

## Architecture

The major/career imagery pipeline becomes:

```text
chart / strength / climate / pattern / remedy / luck-year
-> middle-image activation and strength scoring
-> Bazi spirit-sha calculation and key-position hits
-> spirit-sha-to-middle-image auxiliary weighting
-> discipline group profile
-> constraints for model-assisted modern landing
```

The output should remain under `imagery_analysis.answer_guidance.major_or_career_identification`, adding new structured fields while preserving current ones during migration:

- `spirit_sha_analysis`
- `middle_image_scores`
- `discipline_profile`
- `llm_landing_constraints`

## Bazi Spirit-Sha Scope

First pass spirit-sha coverage:

- `文昌`: learning, textual clarity, documents, exam writing.
- `学堂`: academic training, education, curriculum, scholarly capacity.
- `华盖`: research specialization, solitude, deep study, artistic or technical focus.
- `驿马`: movement, cross-region context, platforms, travel, external communication.
- `桃花/咸池`: expression, social visibility, aesthetics, audience connection.
- `天乙贵人`: help, application support, teacher or institutional assistance.
- `天德/月德`: relief, smoother institutional process, support in exams or applications.
- `禄神`: resources, position, practical support, stable implementation.
- `将星`: organization, rule execution, leadership, public or institutional context.
- `羊刃`: intensity, competition, autonomy, conflict with rules or expression.

Each spirit-sha hit should include:

- `name`
- `branch`
- `basis`, such as day stem, year branch, day branch, or month branch
- `hit_positions`, such as natal year/month/day/hour pillar, current luck pillar, target year pillar
- `strength`, one of `strong`, `medium`, `weak`
- `supports`, a list of middle images or discipline groups it can adjust
- `avoid`, explaining what must not be inferred from it
- `evidence`, with source field paths back to the chart or analysis payload

Key-position rules:

- Day pillar, month pillar, current luck, and target year hits are strongest.
- Year and hour pillar hits are secondary.
- A spirit-sha that exists by rule but hits no relevant position should be weak or omitted from scoring.
- Multiple same-direction hits may stack, but total spirit-sha contribution is capped.

## Middle Images

The middle-image layer should become the main symbolic interface. It should include at least:

- `信息处理`: abstract understanding, data/information handling, system thinking.
- `技能输出`: projects, products, technical or practical output.
- `工程系统`: structure, tools, implementation, modules, repeatable systems.
- `文本表达`: reading, writing, language organization, textual output.
- `制度法理`: rules, law, public norms, qualification systems.
- `人文研究`: interpretation, culture, history, philosophy, academic reading.
- `公共传播`: media, audience connection, public issues, communication.
- `教育训练`: teaching, training, curriculum, knowledge transfer.
- `资源经营`: resource allocation, business, market, management.
- `艺术设计`: aesthetics, visual/content production, creative form.
- `生命健康`: health, medicine, psychology, life-science or care context.
- `研究专精`: deep study, specialization, theory, focused inquiry.
- `跨域迁移`: cross-field integration, external platform, mobility.

Middle-image scoring should separate:

- `base_score`: chart structure, strength, pattern, remedy, and luck-year evidence.
- `spirit_delta`: capped auxiliary adjustment from spirit-sha.
- `question_delta`: user question context adjustment.
- `final_score`: summed score used by the discipline profile.
- `evidence`: structured evidence for each score component.

Spirit-sha must only adjust existing or borderline images. It should not create a high-confidence image without structural support.

## Discipline Profile

The profile is multi-dimensional. It does not force a humanities/STEM binary.

Initial discipline groups:

- `humanities_text`: text, language, literature, history, interpretation.
- `law_public_policy`: law, institutions, public governance, rules.
- `stem_engineering`: engineering, tools, implementation, experiments, technical products.
- `information_data`: information processing, data, models, software/platform logic.
- `business_management`: resources, organization, market, operation, management.
- `media_communication`: expression, audience, communication, public topics.
- `education_training`: teaching, curriculum, training, academic support.
- `arts_design`: aesthetics, form, creative production, design.
- `health_life_science`: health, care, medicine, psychology, life science.
- `cross_domain`: composite mode when two or more groups are close or naturally combine.

Each group should include:

- `score`
- `supporting_images`
- `spirit_factors`
- `structural_evidence`
- `weakening_factors`
- `confidence`

Cross-domain should be true when:

- The top two or three groups are close in score.
- A known combination is structurally supported, such as information plus communication, law plus information, education plus technology, business plus data, or design plus engineering.
- The question context asks for modern majors or careers where cross-domain programs are common.

Examples of profile-to-modern-landing constraints:

- `information_data + media_communication`: allow data journalism, digital media, content platform operations, computational communication.
- `education_training + information_data`: allow educational technology.
- `law_public_policy + information_data`: allow legal technology, compliance technology, data governance.
- `business_management + information_data`: allow information management, business analytics, finance technology.
- `arts_design + stem_engineering`: allow industrial design, architecture-related or interaction design directions, if structural evidence supports design and systems.
- `health_life_science + education_training/humanities_text`: allow psychology, health education, rehabilitation or care-related directions only when health images are structurally supported.

These are constraints for the model, not hardcoded final answers.

## Model And Web-Search Boundary

The prompt should allow the model to use web search or general knowledge to understand modern majors and careers, but only after local symbolic constraints are available.

Rules for the model:

- Use `discipline_profile` as the decision boundary.
- Web search may explain what a modern major or career studies or does.
- Web search must not override the local discipline profile.
- Do not infer a profession from a single spirit-sha.
- Do not infer a profession from a single five-element or ten-god mapping.
- Output at most two real-world landings.
- Each real-world landing must cite the high-scoring discipline groups and middle images it comes from.
- If the top groups are close, prefer a cross-domain landing rather than forcing pure humanities or pure STEM.
- If no group has enough evidence, output uncertainty and ask for real-world feedback instead of listing candidates.

## Output Shape

Example structure:

```json
{
  "middle_image_scores": {
    "信息处理": {
      "base_score": 1.4,
      "spirit_delta": 0.1,
      "question_delta": 0.2,
      "final_score": 1.7,
      "evidence": []
    }
  },
  "spirit_sha_analysis": {
    "active": [
      {
        "name": "文昌",
        "branch": "巳",
        "basis": "day_stem",
        "hit_positions": ["月柱"],
        "strength": "medium",
        "supports": ["文本表达", "教育训练"],
        "avoid": "文昌只增强文书学习象，不直接等同文科专业。",
        "evidence": []
      }
    ],
    "scoring_policy": "神煞为辅助加权，总贡献受上限约束，不能覆盖强弱、格局、病药。"
  },
  "discipline_profile": {
    "groups": [
      {
        "name": "information_data",
        "score": 2.1,
        "supporting_images": ["信息处理", "工程系统"],
        "spirit_factors": [],
        "structural_evidence": [],
        "weakening_factors": [],
        "confidence": "medium"
      },
      {
        "name": "media_communication",
        "score": 1.8,
        "supporting_images": ["文本表达", "公共传播"],
        "spirit_factors": ["桃花增强受众连接"],
        "structural_evidence": [],
        "weakening_factors": [],
        "confidence": "medium"
      }
    ],
    "cross_domain": true,
    "recommended_mode": "信息处理与传播表达的交叉型方向",
    "constraints_for_llm": []
  }
}
```

## Error Handling And Fallbacks

- If spirit-sha rules cannot be calculated, omit `spirit_sha_analysis.active` and add uncertainty; do not fail the whole imagery analysis.
- If the symbolic layer JSON is missing, still produce middle-image scores from chart fields and mark knowledge-source uncertainty.
- If the user question is not a major/career question, do not produce modern landing guidance unless the existing imagery domain needs it.
- If there is no target year, score natal and current age context only; target-year spirit-sha hits should be absent.

## Tests

Add focused tests for:

- Spirit-sha output is structured and evidence-backed.
- 文昌/学堂 can strengthen text or education images but cannot alone make a humanities landing supported.
- 华盖 strengthens research specialization without deciding humanities versus technical research.
- Strong engineering/system evidence remains dominant even when a humanities-related spirit-sha is present.
- Close high scores across two or more groups produce `cross_domain: true`.
- Prompt policy allows model-assisted modern landing but forbids overriding `discipline_profile`.
- Existing major-identification tests continue to pass during migration.

## Migration Notes

Keep current `landing_evidence` and `symbolic_layers` fields for compatibility in the first implementation. Add the new discipline profile beside them. Once prompts and tests consistently use the new profile, modern landing rules can be reduced to examples or constraints rather than direct tool-selected major names.

