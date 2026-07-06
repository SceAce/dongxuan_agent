# Liuyao Real Image And Time Layer Design

## Goal

Add a general Liuyao judgment discipline that makes the model first identify concrete chart evidence, then separate already-formed facts from current triggers and future developments. This must remain domain-neutral and must not specialize the system for finance, work, or any other single question type.

## Scope

This change strengthens interpretation guidance only. It does not change hexagram generation, Najia, useful-god selection, spirit-role calculation, timing candidates, or any calendar conversion rule.

## Principles

The model must first collect hard chart evidence before translating it into domain language. Hard evidence includes useful-god placement, shi/ying placement, month and day effects, void state, moving lines, changed lines, hidden spirits, role-aware combinations, advance/retreat, timing candidates, six spirits, and spirit sha.

The model must split judgment into:

- `already_formed`: conditions suggested by month command, static chart structure, useful-god holding shi or ying, strong visible evidence, and other chart features that describe an existing or already-formed situation.
- `current_trigger`: conditions suggested by day branch, day clash/combine/control/support, void pressure, and any immediate role-aware conflict around shi, ying, or useful gods.
- `future_development`: conditions suggested by moving lines, changed lines, hidden spirits becoming relevant, advance/retreat, three-combination completion, and bounded timing candidates.
- `reversal_pattern`: mixed patterns such as first gain then loss, visible gain with hidden drain, strong useful god under control, weak useful god rescued, or chart evidence that is real but not yet兑现.

Domain templates may translate symbols into the user-facing topic language, but they must not override chart evidence. For example, a domain can translate father-mother into documents, platform rules, reports, or procedures depending on the question, but that translation remains subordinate to useful-god roles, month/day, shi/ying, moving effects, flying-hidden evidence, and completion-chain factors.

## Prompt Contract

The Liuyao prompt must require:

- a `实象主证据` pass before final synthesis;
- an `已然/当前/未然` split;
- explicit handling of static charts as existing structure rather than automatic long-term slowness;
- a warning that month support/control can describe already-formed background and cannot be read only as future outcome;
- a warning that day effects can describe current or near-term triggers;
- domain translation to stay below JSON evidence and not introduce unsupported industry assumptions.

The prompt must keep all existing boundaries:

- JSON remains the only chart source.
- Only enabled advanced layers can be used as evidence.
- Timing remains branch-candidate only and cannot output Gregorian dates.
- Six spirits and spirit sha remain auxiliary.
- Bazi and Daliuren logic remain forbidden.

## Tests

Tests should verify that all question templates expose the common judgment strategy fields and that the prompt requires the real-image and time-layer method. Existing Liuyao tests must continue to pass.
