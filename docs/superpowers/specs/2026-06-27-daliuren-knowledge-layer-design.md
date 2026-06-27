# Daliuren Knowledge Layer Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a layered 大六壬 knowledge structure that lets the agent learn理法、象根、案例中的取象方式，并在分析时优先引用理法约束而不是固定象义。

**Architecture:** Keep the existing knowledge base as the source of truth, but split 大六壬 content into three compiled layers: 理法层 from《大六壬指南》, 象根层 from《五行大义》《六壬取象十二科》, and 案例层 from《邵彦和-大六壬断案新编》《牧夫占验》及现代案例《大六壬经典案例解析》. The agent should consume a small compiled context built from these layers, not raw book text. Modern watermarked PDFs should be normalized into a clean extracted source before indexing, while preserving the original file as archive provenance.

**Tech Stack:** Existing llm-wiki markdown knowledge base, local PDF/text extraction pipeline, Python scripts in the repo, pytest.

---

## File Structure

- Modify `/home/source/Documents/东玄知识库/wiki/topics/大六壬.md`: add a top-level 大六壬 knowledge map with links to 理法、象根、案例、现代案例.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-理法.md`: curated理法总览 from《大六壬指南》.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-象根.md`: curated象根总览 from《五行大义》《六壬取象十二科》.
- Create `/home/source/Documents/东玄知识库/wiki/topics/大六壬-案例总览.md`: curated case index and reading order.
- Create `/home/source/Documents/东玄知识库/wiki/cases/daliuren/*.md`: structured case pages for古案与现代案.
- Create `/home/source/Documents/东玄知识库/wiki/principles/daliuren/*.md`: distilled理法 pages.
- Create `/home/source/Documents/东玄知识库/wiki/images/daliuren/*.md`: distilled象根 pages or概念页 if source pages are not enough.
- Create `/home/source/Documents/东玄知识库/raw/notes/derived_pdf/大六壬/林烽-大六壬经典案例解析-clean.pdf`: clean normalized PDF for indexing.
- Create `/home/source/Documents/东玄知识库/raw/notes/extracted/大六壬/林烽-大六壬经典案例解析-clean.txt`: extracted text from the clean source.
- Create `/home/source/Documents/东玄知识库/wiki/sources/林烽-大六壬经典案例解析-clean.md`: source page that links the archive file and the clean derivation.
- Modify the agent's 大六壬 prompt/context assembly to read the compiled layers instead of raw source pages when available.

---

### Task 1: Map Existing Knowledge Base Coverage

**Files:**
- Read: `/home/source/Documents/东玄知识库/wiki/topics/大六壬.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬指南-(2)-27c880de.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬古课考(1)-da74ca0d.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/大六壬心镜（整理版）-d868f798.md`
- Read: `/home/source/Documents/东玄知识库/wiki/sources/五行大义-渊海子平-core-ocr-1e8c0e8e.md`

- [ ] **Step 1: Confirm current 大六壬 topic pages and source pages already exist**
- [ ] **Step 2: Identify which pages are already useful as理法、案例、象根 inputs**
- [ ] **Step 3: Record gaps where the current wiki only has素材摘要, not a可引用规则页**

### Task 2: Build 理法 Layer From《大六壬指南》

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-理法.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/课体与三传.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/四课与类神.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/旺衰空亡与遁干.md`
- Create: `/home/source/Documents/东玄知识库/wiki/principles/daliuren/象理合参.md`

- [ ] **Step 1: Extract the rule-form passages from《大六壬指南》into one topic page**
  - Include only stable, reusable rules: class selection, transmission logic, strength, emptiness, and when象 must obey理.
- [ ] **Step 2: Split the topic page into small principle pages**
  - Each page should carry one rule family and cite the source page that supports it.
- [ ] **Step 3: Mark which rules are hard rules and which are interpretation heuristics**

### Task 3: Build 象根 Layer From《五行大义》And《六壬取象十二科》

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-象根.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/十二天将象根.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/五行与十二支本义.md`
- Create: `/home/source/Documents/东玄知识库/wiki/images/daliuren/类象边界.md`

- [ ] **Step 1: Extract the象根 that explain why a symbol can be used, not how to force a conclusion**
  - The goal is to preserve source meaning, not to freeze one-to-one fixed symbols.
- [ ] **Step 2: Separate root meaning from later扩展 meaning**
  - Root meaning should be the first lookup.
  - Extended meaning must be labeled as context-dependent.
- [ ] **Step 3: Add explicit boundary notes for symbols that are often overused**
  - Example: avoid turning one symbol into a universal diagnosis or career label.

### Task 4: Build Case Layer For古案与现代案

**Files:**
- Create: `/home/source/Documents/东玄知识库/wiki/topics/大六壬-案例总览.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/邵彦和-断案新编.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/牧夫占验.md`
- Create: `/home/source/Documents/东玄知识库/wiki/cases/daliuren/林烽-大六壬经典案例解析.md`

- [ ] **Step 1: Turn each book into a case index page**
  - Each index page lists major case themes, like illness, litigation, marriage, loss, travel, and timing.
- [ ] **Step 2: Add structured case cards**
  - Case card fields: question, chart features, key rationales, key images, outcome, and transferable technique.
- [ ] **Step 3: Mark which cases are direct exemplars and which are only analogy material**

### Task 5: Normalize The Modern Case PDF

**Files:**
- Read: `/home/source/Documents/东玄/大六壬/02.林烽-《大六壬经典案例解析》109页【666周易网：www.666zhouyi.com】.pdf`
- Read: `/home/source/Documents/东玄/大六壬/2433184671565302.林烽-《大六壬经典案例解析》109页.pdf`
- Create: a clean derived PDF artifact for indexing
- Create: a clean extracted text artifact for the wiki source page
- Modify: `/home/source/Documents/东玄知识库/wiki/sources/林烽-大六壬经典案例解析-clean.md`

- [ ] **Step 1: Prefer the clean PDF copy if it is content-identical**
  - Keep the watermarked file as archive provenance.
- [ ] **Step 2: If needed, produce a dewatermarked derived PDF from the cleanest available source**
  - Do not alter the original file in place.
- [ ] **Step 3: Extract wiki text from the clean source, not from the watermark-heavy version**
  - The purpose is to prevent watermark noise from contaminating case summaries and indexes.
- [ ] **Step 4: Add a source page that records both the archive file and the clean derivation path**
  - Link the archive file `/home/source/Documents/东玄/大六壬/02.林烽-《大六壬经典案例解析》109页【666周易网：www.666zhouyi.com】.pdf`
  - Link the clean file `/home/source/Documents/东玄/大六壬/2433184671565302.林烽-《大六壬经典案例解析》109页.pdf`

### Task 6: Wire Compiled Layers Into Agent Context

**Files:**
- Modify: `daliuren_prompt.md`
- Modify: `daliuren_session.py`
- Modify: `dongxuan_agent/rule_cards.py` or a new knowledge-loading module if needed
- Create: tests for prompt/context parity

- [ ] **Step 1: Make the agent prefer compiled理法/象根/案例 pages when available**
- [ ] **Step 2: Keep raw source pages as fallback evidence, not first-class runtime context**
- [ ] **Step 3: Ensure the output can cite case rationale and principle pages separately**

---

## Self-Review

### Coverage Check

- 理法层 is covered by Task 2.
- 象根层 is covered by Task 3.
- 案例层 is covered by Task 4.
- 现代案例去水印与派生处理 is covered by Task 5.
- Agent wiring is covered by Task 6.

### Consistency Check

- The plan keeps original PDFs intact.
- The clean modern case copy is used for extraction and indexing.
- The compiled pages are layered by function, not by book name alone.

### Scope Check

This is a single sub-project because all work serves one runtime behavior: the 大六壬 agent should learn and cite理法、象根、案例 in a layered way. If the knowledge pages need extensive mass-editing across unrelated术数, that should be a separate plan.
